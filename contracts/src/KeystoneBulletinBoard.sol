// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title KeystoneBulletinBoard
/// @notice Research-only request/deadline/response commitment registry.
/// @dev DLEQ proofs are verified off-chain in the MPP. This contract records
///      canonical timing, member identity, commitments, and response bitmaps.
contract KeystoneBulletinBoard {
    enum RequestKind {
        Audit,
        Dispute
    }

    enum RequestStatus {
        None,
        Open,
        Finalized,
        Cancelled
    }

    struct Epoch {
        bool exists;
        uint16 n;
        uint16 threshold;
        bytes32 publicKeyHash;
        bytes32 membersRoot;
        uint64 activeFrom;
        uint64 activeUntil;
    }

    struct Request {
        RequestKind kind;
        RequestStatus status;
        uint64 epochId;
        bytes32 subjectHash;
        bytes32 verifierSetHash;
        uint64 openedAt;
        uint64 deadline;
        uint16 requiredValid;
        uint16 validAtFinalization;
        uint256 sampledBitmap;
        uint256 responseBitmap;
        uint256 invalidBitmap;
        uint256 equivocationBitmap;
        uint256 missingBitmap;
        bool passed;
    }

    address public admin;

    mapping(uint64 epochId => Epoch) public epochs;
    mapping(uint64 epochId => mapping(uint16 index => address custodian)) public custodians;
    mapping(bytes32 requestId => Request) private requests;
    mapping(bytes32 requestId => mapping(uint16 index => bytes32 commitment)) public responseCommitments;
    mapping(bytes32 requestId => mapping(uint16 index => bytes32 secondCommitment)) public equivocationCommitments;

    event AdminTransferred(address indexed oldAdmin, address indexed newAdmin);
    event EpochRegistered(
        uint64 indexed epochId,
        uint16 n,
        uint16 threshold,
        bytes32 publicKeyHash,
        bytes32 membersRoot,
        uint64 activeFrom,
        uint64 activeUntil
    );
    event RequestOpened(
        bytes32 indexed requestId,
        RequestKind indexed kind,
        uint64 indexed epochId,
        bytes32 subjectHash,
        bytes32 verifierSetHash,
        uint64 deadline,
        uint16 requiredValid,
        uint256 sampledBitmap
    );
    event ResponseCommitted(
        bytes32 indexed requestId,
        uint16 indexed memberIndex,
        address indexed custodian,
        bytes32 responseCommitment,
        uint64 submittedAt
    );
    event EquivocationObserved(
        bytes32 indexed requestId, uint16 indexed memberIndex, bytes32 firstCommitment, bytes32 secondCommitment
    );
    event ResponseMarkedInvalid(bytes32 indexed requestId, uint16 indexed memberIndex, bytes32 evidenceHash);
    event RequestFinalized(
        bytes32 indexed requestId,
        bool passed,
        uint16 validResponses,
        uint256 missingBitmap,
        uint256 invalidBitmap,
        uint256 equivocationBitmap
    );
    event RequestCancelled(bytes32 indexed requestId);

    error OnlyAdmin();
    error InvalidEpoch();
    error InvalidMemberSet();
    error InvalidRequest();
    error InvalidDeadline();
    error NotSampled();
    error WrongCustodian();
    error RequestClosed();
    error DuplicateResponse();
    error TooEarlyToFinalize();

    modifier onlyAdmin() {
        _requireAdmin();
        _;
    }

    function _requireAdmin() internal view {
        if (msg.sender != admin) revert OnlyAdmin();
    }

    constructor(address initialAdmin) {
        require(initialAdmin != address(0), "admin=0");
        admin = initialAdmin;
    }

    function transferAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "admin=0");
        address old = admin;
        admin = newAdmin;
        emit AdminTransferred(old, newAdmin);
    }

    function registerEpoch(
        uint64 epochId,
        uint16 threshold,
        bytes32 publicKeyHash,
        bytes32 membersRoot,
        uint64 activeFrom,
        uint64 activeUntil,
        address[] calldata memberAddresses
    ) external onlyAdmin {
        uint256 n = memberAddresses.length;
        if (
            epochs[epochId].exists || n == 0 || n > 256 || threshold == 0 || threshold > n
                || publicKeyHash == bytes32(0) || membersRoot == bytes32(0) || activeUntil <= activeFrom
        ) revert InvalidMemberSet();

        // The preceding n <= 256 check makes this narrowing conversion safe.
        // forge-lint: disable-next-line(unsafe-typecast)
        uint16 memberCount = uint16(n);

        for (uint16 i = 1; i <= n; i++) {
            address member = memberAddresses[i - 1];
            if (member == address(0)) revert InvalidMemberSet();
            for (uint16 j = 1; j < i; j++) {
                if (memberAddresses[j - 1] == member) revert InvalidMemberSet();
            }
            custodians[epochId][i] = member;
        }

        epochs[epochId] = Epoch({
            exists: true,
            n: memberCount,
            threshold: threshold,
            publicKeyHash: publicKeyHash,
            membersRoot: membersRoot,
            activeFrom: activeFrom,
            activeUntil: activeUntil
        });

        emit EpochRegistered(epochId, memberCount, threshold, publicKeyHash, membersRoot, activeFrom, activeUntil);
    }

    function openAudit(
        bytes32 requestId,
        uint64 epochId,
        bytes32 canaryHash,
        uint256 sampledBitmap,
        uint16 requiredValid,
        uint64 deadline
    ) external onlyAdmin {
        Epoch memory epoch = _activeEpoch(epochId);
        if (sampledBitmap == 0 || _hasBitsOutsideCommittee(sampledBitmap, epoch.n)) {
            revert InvalidRequest();
        }
        uint16 sampleCount = _popcount(sampledBitmap);
        if (requiredValid == 0 || requiredValid > sampleCount) revert InvalidRequest();
        _openRequest(
            requestId, RequestKind.Audit, epochId, canaryHash, bytes32(0), sampledBitmap, requiredValid, deadline
        );
    }

    function openDispute(
        bytes32 requestId,
        uint64 epochId,
        bytes32 recordCommitment,
        bytes32 verifierSetHash,
        uint64 deadline
    ) external onlyAdmin {
        Epoch memory epoch = _activeEpoch(epochId);
        if (verifierSetHash == bytes32(0)) revert InvalidRequest();
        uint256 allMembers = epoch.n == 256 ? type(uint256).max : (uint256(1) << epoch.n) - 1;
        _openRequest(
            requestId,
            RequestKind.Dispute,
            epochId,
            recordCommitment,
            verifierSetHash,
            allMembers,
            epoch.threshold,
            deadline
        );
    }

    function submitResponse(bytes32 requestId, uint16 memberIndex, bytes32 responseCommitment) external {
        Request storage request = requests[requestId];
        if (request.status != RequestStatus.Open || block.timestamp > request.deadline) {
            revert RequestClosed();
        }
        Epoch memory epoch = epochs[request.epochId];
        if (memberIndex == 0 || memberIndex > epoch.n) revert InvalidRequest();
        uint256 bit = uint256(1) << (memberIndex - 1);
        if ((request.sampledBitmap & bit) == 0) revert NotSampled();
        if (custodians[request.epochId][memberIndex] != msg.sender) revert WrongCustodian();
        if (responseCommitment == bytes32(0)) revert InvalidRequest();

        bytes32 first = responseCommitments[requestId][memberIndex];
        if (first == bytes32(0)) {
            responseCommitments[requestId][memberIndex] = responseCommitment;
            request.responseBitmap |= bit;
            emit ResponseCommitted(requestId, memberIndex, msg.sender, responseCommitment, uint64(block.timestamp));
            return;
        }
        if (first == responseCommitment) revert DuplicateResponse();
        if (equivocationCommitments[requestId][memberIndex] != bytes32(0)) {
            revert DuplicateResponse();
        }
        equivocationCommitments[requestId][memberIndex] = responseCommitment;
        request.equivocationBitmap |= bit;
        emit EquivocationObserved(requestId, memberIndex, first, responseCommitment);
    }

    /// @notice Records the outcome of deterministic off-chain proof verification.
    /// @dev A production design can replace admin adjudication with a proof verifier,
    ///      optimistic challenge, or governance process.
    function markInvalidResponse(bytes32 requestId, uint16 memberIndex, bytes32 evidenceHash) external onlyAdmin {
        Request storage request = requests[requestId];
        if (request.status != RequestStatus.Open) revert RequestClosed();
        Epoch memory epoch = epochs[request.epochId];
        if (memberIndex == 0 || memberIndex > epoch.n) revert InvalidRequest();
        if (evidenceHash == bytes32(0)) revert InvalidRequest();
        uint256 bit = uint256(1) << (memberIndex - 1);
        if ((request.responseBitmap & bit) == 0) revert InvalidRequest();
        request.invalidBitmap |= bit;
        emit ResponseMarkedInvalid(requestId, memberIndex, evidenceHash);
    }

    function finalize(bytes32 requestId) external {
        Request storage request = requests[requestId];
        if (request.status != RequestStatus.Open) revert RequestClosed();
        if (block.timestamp <= request.deadline) revert TooEarlyToFinalize();

        uint256 excluded = request.invalidBitmap | request.equivocationBitmap;
        uint256 validBitmap = request.responseBitmap & ~excluded & request.sampledBitmap;
        uint16 valid = _popcount(validBitmap);
        uint256 missing = request.sampledBitmap & ~request.responseBitmap;

        request.status = RequestStatus.Finalized;
        request.validAtFinalization = valid;
        request.missingBitmap = missing;
        request.passed = valid >= request.requiredValid;

        emit RequestFinalized(
            requestId, request.passed, valid, missing, request.invalidBitmap, request.equivocationBitmap
        );
    }

    function cancel(bytes32 requestId) external onlyAdmin {
        Request storage request = requests[requestId];
        if (request.status != RequestStatus.Open) revert RequestClosed();
        request.status = RequestStatus.Cancelled;
        emit RequestCancelled(requestId);
    }

    function getRequest(bytes32 requestId) external view returns (Request memory) {
        return requests[requestId];
    }

    function isSampled(bytes32 requestId, uint16 memberIndex) external view returns (bool) {
        Request storage request = requests[requestId];
        if (memberIndex == 0 || memberIndex > 256) return false;
        return (request.sampledBitmap & (uint256(1) << (memberIndex - 1))) != 0;
    }

    function _activeEpoch(uint64 epochId) internal view returns (Epoch memory epoch) {
        epoch = epochs[epochId];
        if (!epoch.exists || block.timestamp < epoch.activeFrom || block.timestamp > epoch.activeUntil) {
            revert InvalidEpoch();
        }
    }

    function _openRequest(
        bytes32 requestId,
        RequestKind kind,
        uint64 epochId,
        bytes32 subjectHash,
        bytes32 verifierSetHash,
        uint256 sampledBitmap,
        uint16 requiredValid,
        uint64 deadline
    ) internal {
        if (requests[requestId].status != RequestStatus.None || requestId == bytes32(0) || subjectHash == bytes32(0)) {
            revert InvalidRequest();
        }
        if (deadline <= block.timestamp) revert InvalidDeadline();

        requests[requestId] = Request({
            kind: kind,
            status: RequestStatus.Open,
            epochId: epochId,
            subjectHash: subjectHash,
            verifierSetHash: verifierSetHash,
            openedAt: uint64(block.timestamp),
            deadline: deadline,
            requiredValid: requiredValid,
            validAtFinalization: 0,
            sampledBitmap: sampledBitmap,
            responseBitmap: 0,
            invalidBitmap: 0,
            equivocationBitmap: 0,
            missingBitmap: 0,
            passed: false
        });

        emit RequestOpened(
            requestId, kind, epochId, subjectHash, verifierSetHash, deadline, requiredValid, sampledBitmap
        );
    }

    function _hasBitsOutsideCommittee(uint256 bitmap, uint16 n) internal pure returns (bool) {
        if (n == 256) return false;
        return bitmap >> n != 0;
    }

    function _popcount(uint256 value) internal pure returns (uint16 count) {
        while (value != 0) {
            value &= value - 1;
            count++;
        }
    }
}
