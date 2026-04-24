// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AIAgencyEscrow
 * @dev Escrow contract for AI Talent Agency on Kite AI Network.
 * Handles job creation, fund locking, and 20/80 fee distribution.
 */
contract AIAgencyEscrow {
    address public agencyOwner;
    uint256 public constant AGENCY_FEE_PERCENTAGE = 20;

    enum JobStatus { Created, Active, Completed, Refunded }

    struct Job {
        address client;
        address worker;
        uint256 budget;
        JobStatus status;
        string taskDetails;
        uint256 createdAt;
    }

    mapping(uint256 => Job) public jobs;
    uint256 public jobCount;

    event JobCreated(uint256 indexed jobId, address indexed client, uint256 budget);
    event JobAssigned(uint256 indexed jobId, address indexed worker);
    event JobCompleted(uint256 indexed jobId, uint256 workerAmount, uint256 agencyAmount);
    event JobRefunded(uint256 indexed jobId, uint256 amount);

    modifier onlyAgency() {
        require(msg.sender == agencyOwner, "Only agency can call this");
        _;
    }

    constructor() {
        agencyOwner = msg.sender;
    }

    /**
     * @dev User creates a job and deposits native KITE tokens.
     */
    function createJob(string memory _taskDetails) external payable returns (uint256) {
        require(msg.value > 0, "Budget must be greater than 0");

        jobCount++;
        jobs[jobCount] = Job({
            client: msg.sender,
            worker: address(0),
            budget: msg.value,
            status: JobStatus.Created,
            taskDetails: _taskDetails,
            createdAt: block.timestamp
        });

        emit JobCreated(jobCount, msg.sender, msg.value);
        return jobCount;
    }

    /**
     * @dev Agency assigns a worker agent to the job.
     */
    function assignWorker(uint256 _jobId, address _worker) external onlyAgency {
        Job storage job = jobs[_jobId];
        require(job.status == JobStatus.Created, "Job not in Created state");
        require(_worker != address(0), "Invalid worker address");

        job.worker = _worker;
        job.status = JobStatus.Active;

        emit JobAssigned(_jobId, _worker);
    }

    /**
     * @dev Agency releases funds after task completion.
     * Distributes 80% to worker and 20% to agency.
     */
    function completeJob(uint256 _jobId) external onlyAgency {
        Job storage job = jobs[_jobId];
        require(job.status == JobStatus.Active, "Job not Active");
        require(job.worker != address(0), "No worker assigned");

        uint256 agencyAmount = (job.budget * AGENCY_FEE_PERCENTAGE) / 100;
        uint256 workerAmount = job.budget - agencyAmount;

        job.status = JobStatus.Completed;

        (bool successWorker, ) = payable(job.worker).call{value: workerAmount}("");
        require(successWorker, "Transfer to worker failed");

        (bool successAgency, ) = payable(agencyOwner).call{value: agencyAmount}("");
        require(successAgency, "Transfer to agency failed");

        emit JobCompleted(_jobId, workerAmount, agencyAmount);
    }

    /**
     * @dev Agency or Client can refund if job is not completed.
     */
    function refundJob(uint256 _jobId) external {
        Job storage job = jobs[_jobId];
        require(msg.sender == agencyOwner || msg.sender == job.client, "Unauthorized");
        require(job.status == JobStatus.Created || job.status == JobStatus.Active, "Cannot refund");

        uint256 amount = job.budget;
        job.status = JobStatus.Refunded;
        job.budget = 0;

        (bool success, ) = payable(job.client).call{value: amount}("");
        require(success, "Refund failed");

        emit JobRefunded(_jobId, amount);
    }

    // Function to receive funds
    receive() external payable {}
}
