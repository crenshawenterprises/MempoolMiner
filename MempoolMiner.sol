// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "@uniswap/lib/contracts/libraries/UniswapV2Library.sol";
import "@uniswap/v2-periphery/contracts/libraries/UniswapV2OracleLibrary.sol";

contract MempoolMiner {
    using SafeMath for uint256;

    address private owner;
    IUniswapV2Router02 private router;
    address private factory;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function");
        _;
    }

    constructor(IUniswapV2Router02 _router, address _factory) {
        owner = msg.sender;
        router = _router;
        factory = _factory;
    }

    function mineMempool(IERC20 tokenA, IERC20 tokenB, uint256 amountIn, uint256 minProfit) external onlyOwner {
        uint256 balanceBefore = tokenA.balanceOf(address(this));
        tokenA.transferFrom(msg.sender, address(this), amountIn);

        // Get pair for tokenA and tokenB
        address pairAddress = UniswapV2Library.pairFor(factory, address(tokenA), address(tokenB));
        IUniswapV2Pair pair = IUniswapV2Pair(pairAddress);

        // Check for profitable arbitrage opportunity
        (uint reserveA, uint reserveB,) = pair.getReserves();
        uint256 amountOut = UniswapV2Library.getAmountOut(amountIn, reserveA, reserveB);

        require(amountOut >= minProfit, "Minimum profit not reached");

        // Swap tokenA for tokenB on Uniswap
        address[] memory path = new address[](2);
        path[0] = address(tokenA);
        path[1] = address(tokenB);
        tokenA.approve(address(router), amountIn);
        router.swapExactTokensForTokens(amountIn, amountOut, path, address(this), block.timestamp);

        // Profits are now stored in the contract as tokenB
    }

    function withdraw(IERC20 token) external onlyOwner {
        uint256 balance = token.balanceOf(address(this));
        token.transfer(msg.sender, balance);
    }
}
