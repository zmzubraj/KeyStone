// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {KeystoneBulletinBoard} from "../src/KeystoneBulletinBoard.sol";

interface Vm {
    function assume(bool condition) external;
    function expectEmit(bool checkTopic1, bool checkTopic2, bool checkTopic3, bool checkData, address emitter) external;
    function expectRevert(bytes4 revertData) external;
    function pauseGasMetering() external;
    function prank(address sender) external;
    function resumeGasMetering() external;
    function startPrank(address sender) external;
    function stopPrank() external;
    function warp(uint256 newTimestamp) external;
}

contract KeystoneBulletinBoardTest {
    Vm private constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    event RequestFinalized(
        bytes32 indexed requestId,
        bool passed,
        uint16 validResponses,
        uint256 missingBitmap,
        uint256 invalidBitmap,
        uint256 equivocationBitmap
    );
    event RequestCancelled(bytes32 indexed requestId);

    KeystoneBulletinBoard board;
    address[] members;

    function setUp() public {
        board = new KeystoneBulletinBoard(address(this));
        for (uint160 i = 1; i <= 5; i++) {
            members.push(address(i));
        }
        board.registerEpoch(
            1,
            3,
            keccak256("pk"),
            keccak256("members"),
            uint64(block.timestamp),
            uint64(block.timestamp + 7 days),
            members
        );
    }

    function testAuditFinalizesWithMissingBitmap() public {
        bytes32 requestId = keccak256("audit-1");
        uint256 sample = 7;
        board.openAudit(requestId, 1, keccak256("canary"), sample, 3, uint64(block.timestamp + 10));

        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("response-1"));
        VM.prank(members[1]);
        board.submitResponse(requestId, 2, keccak256("response-2"));

        VM.warp(block.timestamp + 11);
        board.finalize(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(!request.passed, "request unexpectedly passed");
        require(request.validAtFinalization == 2, "wrong valid-response count");
        require(request.missingBitmap == 4, "wrong missing bitmap");
    }

    function testEquivocationExcludesResponse() public {
        bytes32 requestId = keccak256("audit-2");
        board.openAudit(requestId, 1, keccak256("canary"), 1, 1, uint64(block.timestamp + 10));

        VM.startPrank(members[0]);
        board.submitResponse(requestId, 1, keccak256("first"));
        board.submitResponse(requestId, 1, keccak256("second"));
        VM.stopPrank();

        VM.warp(block.timestamp + 11);
        board.finalize(requestId);
        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(!request.passed, "equivocating request unexpectedly passed");
        require(request.equivocationBitmap == 1, "wrong equivocation bitmap");
    }

    function testRegisterEpochRejectsDuplicateCustodianIdentity() public {
        address[] memory duplicatedMembers = new address[](3);
        duplicatedMembers[0] = address(101);
        duplicatedMembers[1] = address(102);
        duplicatedMembers[2] = address(101);

        VM.expectRevert(KeystoneBulletinBoard.InvalidMemberSet.selector);
        board.registerEpoch(
            2,
            2,
            keccak256("pk-2"),
            keccak256("members-2"),
            uint64(block.timestamp),
            uint64(block.timestamp + 7 days),
            duplicatedMembers
        );
    }

    function testRegisterEpochRejectsZeroDescriptorCommitments() public {
        address[] memory nextMembers = new address[](3);
        nextMembers[0] = address(101);
        nextMembers[1] = address(102);
        nextMembers[2] = address(103);

        VM.expectRevert(KeystoneBulletinBoard.InvalidMemberSet.selector);
        board.registerEpoch(
            2,
            2,
            bytes32(0),
            keccak256("members-2"),
            uint64(block.timestamp),
            uint64(block.timestamp + 7 days),
            nextMembers
        );

        VM.expectRevert(KeystoneBulletinBoard.InvalidMemberSet.selector);
        board.registerEpoch(
            2, 2, keccak256("pk-2"), bytes32(0), uint64(block.timestamp), uint64(block.timestamp + 7 days), nextMembers
        );
    }

    function testRequestRejectsZeroSubjectBinding() public {
        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(keccak256("audit-zero-subject"), 1, bytes32(0), 1, 1, uint64(block.timestamp + 10));

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openDispute(
            keccak256("dispute-zero-subject"), 1, bytes32(0), keccak256("verifier-set"), uint64(block.timestamp + 10)
        );
    }

    function testInvalidResponseRequiresEvidenceBinding() public {
        bytes32 requestId = keccak256("audit-invalid-evidence");
        board.openAudit(requestId, 1, keccak256("canary-invalid-evidence"), 1, 1, uint64(block.timestamp + 10));

        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("invalid-response"));

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.markInvalidResponse(requestId, 1, bytes32(0));
    }

    // PREAUTHORIZATION_ENGINEERING_QA: these tests exercise only the frozen
    // research bulletin-board boundary and do not establish production security.
    function testAuditFinalizesPassingWithCompleteSample() public {
        bytes32 requestId = keccak256("audit-passing-complete");
        board.openAudit(requestId, 1, keccak256("passing-canary"), 7, 3, uint64(block.timestamp + 10));

        for (uint16 memberIndex = 1; memberIndex <= 3; memberIndex++) {
            VM.prank(members[memberIndex - 1]);
            board.submitResponse(requestId, memberIndex, keccak256(abi.encodePacked("passing-response", memberIndex)));
        }

        VM.warp(block.timestamp + 11);
        VM.expectEmit(true, false, false, true, address(board));
        emit RequestFinalized(requestId, true, 3, 0, 0, 0);
        board.finalize(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(request.status == KeystoneBulletinBoard.RequestStatus.Finalized, "request not finalized");
        require(request.passed, "complete sample did not pass");
        require(request.validAtFinalization == 3, "wrong valid-response count");
        require(request.responseBitmap == 7, "wrong response bitmap");
        require(request.missingBitmap == 0, "complete sample marked missing");
        require(request.invalidBitmap == 0, "unexpected invalid response");
        require(request.equivocationBitmap == 0, "unexpected equivocation");
    }

    function testFinalizeRejectsTooEarlyAndAfterFinalization() public {
        bytes32 requestId = keccak256("audit-finalize-boundaries");
        board.openAudit(requestId, 1, keccak256("finalize-boundary-canary"), 1, 1, uint64(block.timestamp + 10));

        VM.expectRevert(KeystoneBulletinBoard.TooEarlyToFinalize.selector);
        board.finalize(requestId);

        VM.warp(block.timestamp + 11);
        board.finalize(requestId);

        VM.expectRevert(KeystoneBulletinBoard.RequestClosed.selector);
        board.finalize(requestId);
    }

    function testDeadlineEqualityAcceptsResponseButRejectsFinalization() public {
        bytes32 requestId = keccak256("audit-deadline-equality");
        uint64 deadline = uint64(block.timestamp + 10);
        board.openAudit(requestId, 1, keccak256("deadline-equality-canary"), 1, 1, deadline);

        VM.warp(deadline);
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("deadline-equality-response"));

        VM.expectRevert(KeystoneBulletinBoard.TooEarlyToFinalize.selector);
        board.finalize(requestId);

        VM.warp(uint256(deadline) + 1);
        board.finalize(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(request.status == KeystoneBulletinBoard.RequestStatus.Finalized, "deadline request not finalized");
        require(request.passed, "deadline response did not count");
        require(request.validAtFinalization == 1, "deadline response count wrong");
        require(request.missingBitmap == 0, "deadline response marked missing");
    }

    function testResponseAfterDeadlineIsRejectedAndFinalizationRecordsMissing() public {
        bytes32 requestId = keccak256("audit-after-deadline");
        uint64 deadline = uint64(block.timestamp + 10);
        board.openAudit(requestId, 1, keccak256("after-deadline-canary"), 1, 1, deadline);

        VM.warp(uint256(deadline) + 1);
        VM.expectRevert(KeystoneBulletinBoard.RequestClosed.selector);
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("after-deadline-response"));

        board.finalize(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(request.status == KeystoneBulletinBoard.RequestStatus.Finalized, "late request not finalized");
        require(!request.passed, "late response unexpectedly counted");
        require(request.responseBitmap == 0, "late response was recorded");
        require(request.validAtFinalization == 0, "late response affected valid count");
        require(request.missingBitmap == 1, "late response not marked missing");
    }

    function testRequestIdentifiersRejectZeroAndDuplicateOpenRequest() public {
        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(bytes32(0), 1, keccak256("zero-id-canary"), 1, 1, uint64(block.timestamp + 10));

        bytes32 requestId = keccak256("duplicate-open-request");
        board.openAudit(requestId, 1, keccak256("duplicate-open-canary"), 1, 1, uint64(block.timestamp + 10));

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(requestId, 1, keccak256("duplicate-open-canary-2"), 1, 1, uint64(block.timestamp + 20));
    }

    function testRequestIdentifierCannotBeReusedAfterFinalizationOrCancellation() public {
        bytes32 finalizedRequestId = keccak256("reuse-finalized-request");
        board.openAudit(finalizedRequestId, 1, keccak256("reuse-finalized-canary"), 1, 1, uint64(block.timestamp + 10));
        VM.warp(block.timestamp + 11);
        board.finalize(finalizedRequestId);

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(
            finalizedRequestId, 1, keccak256("reuse-finalized-canary-2"), 1, 1, uint64(block.timestamp + 10)
        );

        bytes32 cancelledRequestId = keccak256("reuse-cancelled-request");
        board.openAudit(cancelledRequestId, 1, keccak256("reuse-cancelled-canary"), 1, 1, uint64(block.timestamp + 10));
        board.cancel(cancelledRequestId);

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(
            cancelledRequestId, 1, keccak256("reuse-cancelled-canary-2"), 1, 1, uint64(block.timestamp + 10)
        );
    }

    function testCancelledRequestRejectsSubmissionAndFinalization() public {
        bytes32 requestId = keccak256("cancelled-request-closed");
        board.openAudit(requestId, 1, keccak256("cancelled-request-canary"), 1, 1, uint64(block.timestamp + 10));

        VM.expectEmit(true, false, false, false, address(board));
        emit RequestCancelled(requestId);
        board.cancel(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(request.status == KeystoneBulletinBoard.RequestStatus.Cancelled, "request not cancelled");
        require(request.validAtFinalization == 0, "cancelled request has valid count");
        require(request.missingBitmap == 0, "cancelled request has missing bitmap");
        require(!request.passed, "cancelled request passed");

        VM.expectRevert(KeystoneBulletinBoard.RequestClosed.selector);
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("cancelled-response"));

        VM.expectRevert(KeystoneBulletinBoard.RequestClosed.selector);
        board.finalize(requestId);
    }

    function testDisputeCompletesThresholdResponseLifecycle() public {
        bytes32 requestId = keccak256("dispute-complete-lifecycle");
        bytes32 verifierSetHash = keccak256("dispute-verifier-set");
        board.openDispute(
            requestId, 1, keccak256("dispute-record-commitment"), verifierSetHash, uint64(block.timestamp + 10)
        );

        for (uint16 memberIndex = 1; memberIndex <= 3; memberIndex++) {
            VM.prank(members[memberIndex - 1]);
            board.submitResponse(requestId, memberIndex, keccak256(abi.encodePacked("dispute-response", memberIndex)));
        }

        VM.warp(block.timestamp + 11);
        VM.expectEmit(true, false, false, true, address(board));
        emit RequestFinalized(requestId, true, 3, 24, 0, 0);
        board.finalize(requestId);

        KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);
        require(request.kind == KeystoneBulletinBoard.RequestKind.Dispute, "wrong request kind");
        require(request.status == KeystoneBulletinBoard.RequestStatus.Finalized, "dispute not finalized");
        require(request.verifierSetHash == verifierSetHash, "wrong verifier-set binding");
        require(request.requiredValid == 3, "wrong dispute threshold");
        require(request.sampledBitmap == 31, "wrong dispute member bitmap");
        require(request.responseBitmap == 7, "wrong dispute response bitmap");
        require(request.validAtFinalization == 3, "wrong dispute valid count");
        require(request.missingBitmap == 24, "wrong dispute missing bitmap");
        require(request.passed, "threshold dispute did not pass");
    }

    function testFuzzRegisterEpochRejectsDuplicateCustodianIdentity(uint8 duplicateSource) public {
        address[] memory candidateMembers = new address[](5);
        for (uint160 i = 0; i < 5; i++) {
            candidateMembers[i] = address(101 + i);
        }
        candidateMembers[4] = candidateMembers[uint256(duplicateSource) % 4];

        VM.expectRevert(KeystoneBulletinBoard.InvalidMemberSet.selector);
        board.registerEpoch(
            2,
            3,
            keccak256("fuzz-pk"),
            keccak256("fuzz-members"),
            uint64(block.timestamp),
            uint64(block.timestamp + 7 days),
            candidateMembers
        );
    }

    function testFuzzAuditRejectsThresholdAboveSample(uint256 rawBitmap) public {
        uint256 sample = rawBitmap & 31;
        if (sample == 0) sample = 1;
        uint16 sampledMembers = _popcount(sample);

        VM.expectRevert(KeystoneBulletinBoard.InvalidRequest.selector);
        board.openAudit(
            keccak256(abi.encodePacked("fuzz-audit", rawBitmap)),
            1,
            keccak256(abi.encodePacked("fuzz-canary", rawBitmap)),
            sample,
            sampledMembers + 1,
            uint64(block.timestamp + 10)
        );
    }

    function testFuzzUnauthorizedCallerCannotOpenAudit(address caller) public {
        VM.assume(caller != address(this));

        VM.expectRevert(KeystoneBulletinBoard.OnlyAdmin.selector);
        VM.prank(caller);
        board.openAudit(
            keccak256(abi.encodePacked("unauthorized", caller)),
            1,
            keccak256(abi.encodePacked("unauthorized-canary", caller)),
            1,
            1,
            uint64(block.timestamp + 10)
        );
    }

    function testGas_RegisterEpochFiveMembers() public {
        VM.pauseGasMetering();
        address[] memory nextMembers = new address[](5);
        for (uint160 i = 0; i < 5; i++) {
            nextMembers[i] = address(101 + i);
        }
        VM.resumeGasMetering();

        board.registerEpoch(
            2,
            3,
            keccak256("gas-pk"),
            keccak256("gas-members"),
            uint64(block.timestamp),
            uint64(block.timestamp + 7 days),
            nextMembers
        );
    }

    function testGas_OpenAuditThreeMembers() public {
        board.openAudit(keccak256("gas-open-audit"), 1, keccak256("gas-canary"), 7, 3, uint64(block.timestamp + 10));
    }

    function testGas_SubmitAuditResponse() public {
        VM.pauseGasMetering();
        bytes32 requestId = keccak256("gas-submit-response");
        board.openAudit(requestId, 1, keccak256("gas-submit-canary"), 1, 1, uint64(block.timestamp + 10));
        VM.resumeGasMetering();

        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("gas-response"));
    }

    function testGas_MarkInvalidResponse() public {
        VM.pauseGasMetering();
        bytes32 requestId = keccak256("gas-mark-invalid");
        board.openAudit(requestId, 1, keccak256("gas-invalid-canary"), 1, 1, uint64(block.timestamp + 10));
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("gas-invalid-response"));
        VM.resumeGasMetering();

        board.markInvalidResponse(requestId, 1, keccak256("gas-invalid-evidence"));
    }

    function testGas_RecordEquivocation() public {
        VM.pauseGasMetering();
        bytes32 requestId = keccak256("gas-equivocation");
        board.openAudit(requestId, 1, keccak256("gas-equivocation-canary"), 1, 1, uint64(block.timestamp + 10));
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("gas-first-response"));
        VM.resumeGasMetering();

        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("gas-second-response"));
    }

    function testGas_FinalizeAudit() public {
        VM.pauseGasMetering();
        bytes32 requestId = keccak256("gas-finalize-audit");
        board.openAudit(requestId, 1, keccak256("gas-finalize-canary"), 7, 3, uint64(block.timestamp + 10));
        VM.prank(members[0]);
        board.submitResponse(requestId, 1, keccak256("gas-finalize-response-1"));
        VM.prank(members[1]);
        board.submitResponse(requestId, 2, keccak256("gas-finalize-response-2"));
        VM.warp(block.timestamp + 11);
        VM.resumeGasMetering();

        board.finalize(requestId);
    }

    function testGas_OpenDispute() public {
        board.openDispute(
            keccak256("gas-open-dispute"),
            1,
            keccak256("gas-record"),
            keccak256("gas-verifier-set"),
            uint64(block.timestamp + 10)
        );
    }

    function testGas_CancelRequest() public {
        VM.pauseGasMetering();
        bytes32 requestId = keccak256("gas-cancel");
        board.openAudit(requestId, 1, keccak256("gas-cancel-canary"), 1, 1, uint64(block.timestamp + 10));
        VM.resumeGasMetering();

        board.cancel(requestId);
    }

    function _popcount(uint256 value) internal pure returns (uint16 count) {
        while (value != 0) {
            value &= value - 1;
            count++;
        }
    }
}

contract KeystoneBulletinBoardHandler {
    Vm private constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    KeystoneBulletinBoard private immutable BOARD;
    bytes32[] public requestIds;
    uint256 private nonce;

    constructor(KeystoneBulletinBoard board_) {
        BOARD = board_;
    }

    function requestCount() external view returns (uint256) {
        return requestIds.length;
    }

    function open(uint64 deadlineDelta, bytes32 subjectSeed) external {
        if (block.timestamp > type(uint64).max - 1 days - 1) return;
        bytes32 requestId = keccak256(abi.encodePacked("invariant-audit", nonce++));
        bytes32 subject = subjectSeed == bytes32(0) ? bytes32(uint256(1)) : subjectSeed;
        uint64 deadline = uint64(block.timestamp + 1 + (deadlineDelta % 1 days));
        BOARD.openAudit(requestId, 1, subject, 1, 1, deadline);
        requestIds.push(requestId);
    }

    function respond(uint256 requestIndex, bytes32 commitmentSeed) external {
        if (requestIds.length == 0) return;
        bytes32 requestId = requestIds[requestIndex % requestIds.length];
        KeystoneBulletinBoard.Request memory request = BOARD.getRequest(requestId);
        if (
            request.status != KeystoneBulletinBoard.RequestStatus.Open || block.timestamp > request.deadline
                || request.responseBitmap != 0
        ) return;
        bytes32 commitment = commitmentSeed == bytes32(0) ? bytes32(uint256(1)) : commitmentSeed;
        BOARD.submitResponse(requestId, 1, commitment);
    }

    function equivocate(uint256 requestIndex, bytes32 firstSeed, bytes32 secondSeed) external {
        if (requestIds.length == 0) return;
        bytes32 requestId = requestIds[requestIndex % requestIds.length];
        KeystoneBulletinBoard.Request memory request = BOARD.getRequest(requestId);
        if (
            request.status != KeystoneBulletinBoard.RequestStatus.Open || block.timestamp > request.deadline
                || request.equivocationBitmap != 0
        ) return;

        bytes32 first = firstSeed == bytes32(0) ? bytes32(uint256(1)) : firstSeed;
        bytes32 second = secondSeed == bytes32(0) ? bytes32(uint256(2)) : secondSeed;
        if (second == first) second = bytes32(uint256(second) + 1);

        if (request.responseBitmap == 0) BOARD.submitResponse(requestId, 1, first);
        BOARD.submitResponse(requestId, 1, second);
    }

    function markInvalid(uint256 requestIndex, bytes32 evidenceSeed) external {
        if (requestIds.length == 0) return;
        bytes32 requestId = requestIds[requestIndex % requestIds.length];
        KeystoneBulletinBoard.Request memory request = BOARD.getRequest(requestId);
        if (request.status != KeystoneBulletinBoard.RequestStatus.Open || request.responseBitmap == 0) return;
        bytes32 evidence = evidenceSeed == bytes32(0) ? bytes32(uint256(1)) : evidenceSeed;
        BOARD.markInvalidResponse(requestId, 1, evidence);
    }

    function finalize(uint256 requestIndex) external {
        if (requestIds.length == 0) return;
        bytes32 requestId = requestIds[requestIndex % requestIds.length];
        KeystoneBulletinBoard.Request memory request = BOARD.getRequest(requestId);
        if (request.status != KeystoneBulletinBoard.RequestStatus.Open) return;
        if (block.timestamp <= request.deadline) VM.warp(uint256(request.deadline) + 1);
        BOARD.finalize(requestId);
    }

    function cancel(uint256 requestIndex) external {
        if (requestIds.length == 0) return;
        bytes32 requestId = requestIds[requestIndex % requestIds.length];
        KeystoneBulletinBoard.Request memory request = BOARD.getRequest(requestId);
        if (request.status != KeystoneBulletinBoard.RequestStatus.Open) return;
        BOARD.cancel(requestId);
    }
}

contract KeystoneBulletinBoardInvariantTest {
    KeystoneBulletinBoard private board;
    KeystoneBulletinBoardHandler private handler;
    address[] private invariantTargets;

    function setUp() public {
        board = new KeystoneBulletinBoard(address(this));
        handler = new KeystoneBulletinBoardHandler(board);

        address[] memory oneMember = new address[](1);
        oneMember[0] = address(handler);
        board.registerEpoch(
            1,
            1,
            keccak256("invariant-pk"),
            keccak256("invariant-members"),
            uint64(block.timestamp),
            uint64(block.timestamp + 365 days),
            oneMember
        );
        board.transferAdmin(address(handler));
        invariantTargets.push(address(handler));
    }

    function targetContracts() external view returns (address[] memory) {
        return invariantTargets;
    }

    function invariant_AdminRemainsNonzero() public view {
        require(board.admin() != address(0), "admin became zero");
    }

    function invariant_ResponseAndOutcomeBitmapsRemainConsistent() public view {
        uint256 count = handler.requestCount();
        for (uint256 i = 0; i < count; i++) {
            bytes32 requestId = handler.requestIds(i);
            KeystoneBulletinBoard.Request memory request = board.getRequest(requestId);

            require((request.responseBitmap & ~request.sampledBitmap) == 0, "response outside sample");
            require((request.invalidBitmap & ~request.responseBitmap) == 0, "invalid without response");
            require((request.equivocationBitmap & ~request.responseBitmap) == 0, "equivocation without response");

            if (request.status == KeystoneBulletinBoard.RequestStatus.Finalized) {
                uint256 expectedMissing = request.sampledBitmap & ~request.responseBitmap;
                uint256 excluded = request.invalidBitmap | request.equivocationBitmap;
                uint16 expectedValid = request.responseBitmap & ~excluded == 0 ? 0 : 1;
                require(request.missingBitmap == expectedMissing, "wrong missing bitmap");
                require(request.validAtFinalization == expectedValid, "wrong valid count");
                require(request.passed == (expectedValid >= request.requiredValid), "wrong finalized outcome");
            } else {
                require(request.validAtFinalization == 0, "premature valid count");
                require(request.missingBitmap == 0, "premature missing bitmap");
                require(!request.passed, "premature pass");
            }
        }
    }
}
