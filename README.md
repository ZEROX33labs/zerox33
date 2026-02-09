# ZEROX33

**ERC404 on MegaETH** — 128 Animated 3D Cube NFTs across 16 Trait Categories

[![Website](https://img.shields.io/badge/Web-zerox33.xyz-141416?style=flat-square)](https://zerox33.xyz)
[![Twitter](https://img.shields.io/badge/X-@zerox33labs-141416?style=flat-square)](https://x.com/zerox33labs)
[![Chain](https://img.shields.io/badge/Chain-MegaETH%204326-141416?style=flat-square)](https://megaeth.blockscout.com)

---

## Overview

ZEROX33 is an ERC404 hybrid token (ERC20 + ERC721) deployed on MegaETH, the first real-time blockchain. Each whole token is paired with a unique animated 3D cube NFT.

- **Supply:** 5,012 tokens
- **Images:** 128 unique animated GIFs
- **Traits:** 16 categories including 2 rare Z-RARE tiers
- **Mint Price:** 0.1 ETH per spawn (4 tokens)
- **Chain:** MegaETH (Chain ID: 4326)

## Traits

| Range | Trait | Style |
|-------|-------|-------|
| 0–7 | KERNEL | Deep red/maroon |
| 8–15 | DAEMON | Warm copper |
| 16–23 | THREAD | Amber gold |
| 24–31 | SOCKET | Olive sage |
| 32–39 | SIGNAL | Muted forest |
| 40–47 | PIPE | Teal |
| 48–55 | MUTEX | Steel blue |
| 56–63 | BUFFER | Navy |
| 64–71 | STACK | Deep violet |
| 72–79 | HEAP | Plum |
| 80–87 | CACHE | Mauve |
| 88–95 | FORK | Rose |
| 96–103 | EXEC | Monochrome warm |
| 104–111 | SWAP | Monochrome cool |
| 112–119 | **Z-RARE-I** | ★ White bg, black cubes, Z watermark |
| 120–127 | **Z-RARE-II** | ★ White bg, black cubes, Z watermark |

## Contract

- **Standard:** ERC404 (Hybrid ERC20/ERC721)
- **Solidity:** ^0.8.20
- **Explorer:** [View on Blockscout](https://megaeth.blockscout.com)

### Key Functions

| Function | Description |
|----------|-------------|
| `spawn33()` | Mint 4 ZEROX33 tokens (payable, 0.1 ETH) |
| `tokenBalance()` | Remaining tokens in contract |
| `ownedTokens(address)` | NFTs owned by address |
| `tokenURI(uint256)` | Returns metadata + image for token ID |

## Project Structure

```
zerox33/
├── index.html              # Frontend (static, single file)
├── ZeroX33.sol             # Smart contract
├── generate_zerox33.py     # GIF generator script
├── manifest.json           # Trait mapping (128 entries)
└── assets/
    ├── 0.gif – 127.gif     # 128 animated cube GIFs
    └── logo.png            # ZEROX33 logo
```

## Generate Art

Requires Python 3.8+ and Pillow:

```bash
pip install Pillow
python generate_zerox33.py
```

Generates all 128 animated GIFs into `./assets/` (~1-2 minutes).

## Deploy

1. Deploy `ZeroX33.sol` on MegaETH via Remix or Foundry
2. Update `CONTRACT_ADDRESS` in `index.html`
3. Call `setDataURI("https://zerox33.xyz/assets/")` on the contract
4. Host as static site (Render, Vercel, etc.)

## Links

- **Website:** [zerox33.xyz](https://zerox33.xyz)
- **Twitter/X:** [@zerox33labs](https://x.com/zerox33labs)
- **Explorer:** [MegaETH Blockscout](https://megaeth.blockscout.com)

## License

UNLICENSED
