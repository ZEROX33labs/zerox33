// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

/**
 ZEROX33 — ERC404 on MegaETH
 Supply: 5012 | 128 Animated Cubes | 16 Trait Categories
 
 Website: https://zerox33.xyz
 Twitter: https://x.com/zerox33labs
 Chain:   MegaETH (4326)
*/

abstract contract Ownable {
    event OwnershipTransferred(address indexed user, address indexed newOwner);
    event TokensDeposited(address indexed from, uint256 amount);
    error Unauthorized();
    error InvalidOwner();
    address public owner;
    modifier onlyOwner() { if (msg.sender != owner) revert Unauthorized(); _; }
    constructor(address _owner) {
        if (_owner == address(0)) revert InvalidOwner();
        owner = _owner;
        emit OwnershipTransferred(address(0), _owner);
    }
    function transferOwnership(address _owner) public virtual onlyOwner {
        if (_owner == address(0)) revert InvalidOwner();
        owner = _owner;
        emit OwnershipTransferred(msg.sender, _owner);
    }
    function revokeOwnership() public virtual onlyOwner {
        owner = address(0);
        emit OwnershipTransferred(msg.sender, address(0));
    }
}

abstract contract ERC721Receiver {
    function onERC721Received(address,address,uint256,bytes calldata) external virtual returns (bytes4) {
        return ERC721Receiver.onERC721Received.selector;
    }
}

abstract contract ERC404 is Ownable {
    event ERC20Transfer(address indexed from, address indexed to, uint256 amount);
    event Approval(address indexed owner, address indexed spender, uint256 amount);
    event Transfer(address indexed from, address indexed to, uint256 indexed id);
    event ERC721Approval(address indexed owner, address indexed spender, uint256 indexed id);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    error NotFound(); error AlreadyExists(); error InvalidRecipient();
    error InvalidSender(); error UnsafeRecipient();

    string public name;
    string public symbol;
    uint8 public immutable decimals;
    uint256 public immutable totalSupply;
    uint256 public minted;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(uint256 => address) public getApproved;
    mapping(address => mapping(address => bool)) public isApprovedForAll;
    mapping(uint256 => address) internal _ownerOf;
    mapping(address => uint256[]) internal _owned;
    mapping(uint256 => uint256) internal _ownedIndex;
    mapping(address => bool) public whitelist;
    address public stakingContract;

    constructor(string memory _name, string memory _symbol, uint8 _decimals, uint256 _totalNativeSupply, address _owner) Ownable(_owner) {
        name = _name; symbol = _symbol; decimals = _decimals;
        totalSupply = _totalNativeSupply * (10 ** decimals);
    }

    function setWhitelist(address target, bool state) public onlyOwner { whitelist[target] = state; }

    function ownerOf(uint256 id) public view virtual returns (address o) {
        o = _ownerOf[id]; if (o == address(0)) revert NotFound();
    }

    function withdrawAll() public virtual onlyOwner {
        uint256 b = address(this).balance; require(b > 0, "Zero"); payable(owner).transfer(b);
    }

    function depositTokens(uint256 amount) public onlyOwner {
        _transfer(msg.sender, address(this), amount);
        emit TokensDeposited(msg.sender, amount);
    }

    function tokenURI(uint256 id) public view virtual returns (string memory);

    function approve(address spender, uint256 amountOrId) public virtual returns (bool) {
        if (amountOrId <= minted && amountOrId > 0) {
            address o = _ownerOf[amountOrId];
            if (msg.sender != o && !isApprovedForAll[o][msg.sender]) revert Unauthorized();
            getApproved[amountOrId] = spender;
            emit Approval(o, spender, amountOrId);
        } else {
            allowance[msg.sender][spender] = amountOrId;
            emit Approval(msg.sender, spender, amountOrId);
        }
        return true;
    }

    function setApprovalForAll(address op, bool ok) public virtual {
        isApprovedForAll[msg.sender][op] = ok;
        emit ApprovalForAll(msg.sender, op, ok);
    }

    function transferFrom(address from, address to, uint256 amountOrId) public virtual {
        if (amountOrId <= minted) {
            if (from != _ownerOf[amountOrId]) revert InvalidSender();
            if (to == address(0)) revert InvalidRecipient();
            if (msg.sender != from && !isApprovedForAll[from][msg.sender] &&
                msg.sender != getApproved[amountOrId] && msg.sender != stakingContract) revert Unauthorized();
            balanceOf[from] -= _getUnit();
            unchecked { balanceOf[to] += _getUnit(); }
            _ownerOf[amountOrId] = to;
            delete getApproved[amountOrId];
            uint256 uid = _owned[from][_owned[from].length - 1];
            _owned[from][_ownedIndex[amountOrId]] = uid;
            _owned[from].pop();
            _ownedIndex[uid] = _ownedIndex[amountOrId];
            _owned[to].push(amountOrId);
            _ownedIndex[amountOrId] = _owned[to].length - 1;
            emit Transfer(from, to, amountOrId);
            emit ERC20Transfer(from, to, _getUnit());
        } else {
            uint256 a = allowance[from][msg.sender];
            if (a != type(uint256).max) allowance[from][msg.sender] = a - amountOrId;
            _transfer(from, to, amountOrId);
        }
    }

    function transfer(address to, uint256 amount) public virtual returns (bool) { return _transfer(msg.sender, to, amount); }

    function safeTransferFrom(address from, address to, uint256 id) public virtual {
        transferFrom(from, to, id);
        if (to.code.length != 0 && ERC721Receiver(to).onERC721Received(msg.sender, from, id, "") != ERC721Receiver.onERC721Received.selector) revert UnsafeRecipient();
    }

    function safeTransferFrom(address from, address to, uint256 id, bytes calldata data) public virtual {
        transferFrom(from, to, id);
        if (to.code.length != 0 && ERC721Receiver(to).onERC721Received(msg.sender, from, id, data) != ERC721Receiver.onERC721Received.selector) revert UnsafeRecipient();
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 unit = _getUnit();
        uint256 bbs = balanceOf[from]; uint256 bbr = balanceOf[to];
        balanceOf[from] -= amount;
        unchecked { balanceOf[to] += amount; }
        if (!whitelist[from]) { uint256 tb = (bbs/unit) - (balanceOf[from]/unit); for (uint256 i=0; i<tb; i++) _burn(from); }
        if (!whitelist[to]) { uint256 tm = (balanceOf[to]/unit) - (bbr/unit); for (uint256 i=0; i<tm; i++) _mint(to); }
        emit ERC20Transfer(from, to, amount);
        return true;
    }

    function _getUnit() internal view returns (uint256) { return 10 ** decimals; }

    function _mint(address to) internal virtual {
        if (to == address(0)) revert InvalidRecipient();
        unchecked { minted++; }
        uint256 id = minted;
        if (_ownerOf[id] != address(0)) revert AlreadyExists();
        _ownerOf[id] = to; _owned[to].push(id); _ownedIndex[id] = _owned[to].length - 1;
        emit Transfer(address(0), to, id);
    }

    function _burn(address from) internal virtual {
        if (from == address(0)) revert InvalidSender();
        uint256 id = _owned[from][_owned[from].length - 1];
        _owned[from].pop(); delete _ownedIndex[id]; delete _ownerOf[id]; delete getApproved[id];
        emit Transfer(from, address(0), id);
    }

    function _setNameSymbol(string memory _n, string memory _s) internal { name = _n; symbol = _s; }
}

library Strings {
    function toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 t = value; uint256 d;
        while (t != 0) { d++; t /= 10; }
        bytes memory b = new bytes(d);
        while (value != 0) { d--; b[d] = bytes1(uint8(48 + value % 10)); value /= 10; }
        return string(b);
    }
}

contract ZeroX33 is ERC404 {
    uint256 public totalBurned;
    uint256 public lastBurnTime;
    uint256 public burnInterval = 1 days;
    uint256 public burnAmount = 50 * 10**16;
    uint256 public mintPrice = 0.1 ether;
    string public dataURI;
    string public baseTokenURI;
    bool public isSpawnEnabled;

    // 16 trait names
    string[16] private TRAIT_NAMES = [
        "KERNEL","DAEMON","THREAD","SOCKET","SIGNAL","PIPE","MUTEX","BUFFER",
        "STACK","HEAP","CACHE","FORK","EXEC","SWAP","Z-RARE-I","Z-RARE-II"
    ];

    constructor(address _owner) ERC404("ZEROX33", "0X33", 18, 5012, _owner) {
        balanceOf[address(this)] = 2506 * 10**18;
        balanceOf[_owner] = 2506 * 10**18;
        stakingContract = address(0);
        setWhitelist(address(this), true);
        isSpawnEnabled = true;
        lastBurnTime = block.timestamp;
    }

    receive() external payable {}

    function setStakingContract(address _s) external onlyOwner { stakingContract = _s; }
    function setDataURI(string memory _d) public onlyOwner { dataURI = _d; }
    function setTokenURI(string memory _t) public onlyOwner { baseTokenURI = _t; }
    function setMintPrice(uint256 _p) public onlyOwner { mintPrice = _p; }
    function toggleSpawn() public onlyOwner { isSpawnEnabled = !isSpawnEnabled; }
    function setNameSymbol(string memory _n, string memory _s) public onlyOwner { _setNameSymbol(_n, _s); }

    function withdrawAll() public override onlyOwner {
        uint256 b = address(this).balance; require(b > 0, "Zero"); payable(owner).transfer(b);
    }

    function withdrawTokens(uint256 amount) public onlyOwner {
        require(balanceOf[address(this)] >= amount, "Insufficient");
        _transfer(address(this), owner, amount);
        emit ERC20Transfer(address(this), owner, amount);
    }

    function autoBurn() external onlyOwner {
        uint256 elapsed = block.timestamp - lastBurnTime;
        uint256 intervals = elapsed / burnInterval;
        if (intervals > 0) {
            uint256 amt = intervals * burnAmount;
            balanceOf[address(this)] -= amt;
            totalBurned += amt;
            lastBurnTime = block.timestamp;
            emit Transfer(address(this), address(0), amt);
        }
    }

    function spawn33() public payable {
        require(isSpawnEnabled, "Disabled");
        require(msg.value >= mintPrice, "Insufficient");
        uint256 claim = 4 * _getUnit();
        require(balanceOf[address(this)] >= claim, "Sold out");
        _transfer(address(this), msg.sender, claim);
        payable(owner).transfer(msg.value);
    }

    function tokenBalance() public view returns (uint256) { return balanceOf[address(this)] / _getUnit(); }
    function contractBalance() public view returns (uint256) { return address(this).balance; }
    function ownedTokens(address _o) public view returns (uint256[] memory) { return _owned[_o]; }

    function tokenURI(uint256 id) public view override returns (string memory) {
        if (bytes(baseTokenURI).length > 0) {
            return string.concat(baseTokenURI, Strings.toString(id));
        }
        // Determine image index (0-127) and trait
        uint256 seed = uint256(keccak256(abi.encodePacked(id)));
        uint256 imageIdx = seed % 128;
        uint256 traitIdx = imageIdx / 8;  // 0-15
        uint256 variation = imageIdx % 8; // 0-7

        string memory image = string.concat(Strings.toString(imageIdx), ".gif");
        string memory traitName = TRAIT_NAMES[traitIdx];

        return string.concat(
            "data:application/json;utf8,",
            '{"name":"ZEROX33 #', Strings.toString(id),
            '","description":"ZEROX33 ERC404 on MegaETH. 128 animated 3D cubes, 16 trait categories.","external_url":"https://zerox33.xyz","image":"',
            dataURI, image,
            '","attributes":[{"trait_type":"Process","value":"', traitName,
            '"},{"trait_type":"Variation","value":"', Strings.toString(variation),
            '"},{"trait_type":"Image","value":"', Strings.toString(imageIdx),
            '"}]}'
        );
    }
}
