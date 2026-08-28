// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {KeystoneBulletinBoard} from "../src/KeystoneBulletinBoard.sol";

interface Vm {
    function prank(address sender) external;
    function startPrank(address sender) external;
    function stopPrank() external;
    function warp(uint256 newTimestamp) external;
}

contract KeystoneBulletinBoardTest {
    Vm private constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

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
        board.openAudit(
            requestId,
            1,
            keccak256("canary"),
            sample,
            3,
            uint64(block.timestamp + 10)
        );

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
        board.openAudit(
            requestId,
            1,
            keccak256("canary"),
            1,
            1,
            uint64(block.timestamp + 10)
        );

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
}
