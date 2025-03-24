# Flower CEC (Cloud-Edge-Client Continuum)

## Publications

- **Enabling Flower for Federated Learning in Web Browsers in the Cloud-Edge-Client Continuum.**  M. Colosi, A. Catalfamo, M. Garofalo, and M. Villari. In Proceedings of the *IEEE/ACM 17th International Conference on Utility and Cloud Computing (UCC 2024)*. [https://doi.org/10.1109/UCC63386.2024.00048](https://doi.org/10.1109/UCC63386.2024.00048)

Related work:
- **Cloud-Edge-Client Continuum: Leveraging Browsers as Deployment Nodes with Virtual Pods.** M. Colosi, M. Garofalo, A. Galletta, M. Fazio, A. Celesti, and M. Villari. 2024. In Proceedings of the *IEEE/ACM 10th International Conference on Big Data Computing, Applications and Technologies (BDCAT '23)*. [https://doi.org/10.1145/3632366.3632395](https://doi.org/10.1145/3632366.3632395)
- **Web-Centric Federated Learning over the Cloud-Edge Continuum Leveraging ONNX and WASM.** M. Garofalo, M. Colosi, A. Catalfamo, and M. Villari. In Proceedings of  the*IEEE 29th IEEE Symposium on Computers and Communications (ISCC2024), June 26--29, 2024, Paris, France.* doi: [https://doi.org/10.1109/ISCC61673.2024.10733614](https://doi.org/10.1109/ISCC61673.2024.10733614)

## Overview

This repository implements a solution that seamlessly integrates the Flower framework with Web browsers for federated learning (FL). The system is designed to harness the computational power of heterogeneous devices (laptops, smartphones, etc.) without requiring dependency installations or manual configurations on client devices. Instead, the approach leverages a Cloud-Edge-Client Continuum architecture along with the Flower-Client Virtual Pod to transparently manage communication between the central aggregator (Flower Server) and remote Web-based FL clients.

## How It Works

### Cloud-Edge-Client Continuum

The solution adopts the Cloud-Edge-Client Continuum paradigm, which extends traditional cloud and edge computing infrastructures to include client devices as active nodes. In this architecture:
- **Cloud** handles centralized coordination and data aggregation.
- **Edge** provides localized processing near data sources.
- **Client devices** (via Web browsers) join the continuum with zero additional configuration, contributing their computational resources seamlessly.

This continuum approach abstracts the traditional client-server model, enabling dynamic, on-the-fly cluster formation by leveraging widely available devices.

### Flower-Client Virtual Pod

A core component of this solution is the Flower-Client Virtual Pod (VPod). The VPod:
- Acts as an intermediary between the Flower Server (aggregator) and the FL Web Clients.
- Implements a Virtual Flower-Client (VFC) that communicates with the Flower Server using standard Flower methods (e.g., get_parameters, fit, evaluate).
- Manages communication through a bidirectional proxy, ensuring that training computations occur within the Web browser while the Flower Server remains unaware of the underlying client implementation.
- Allows multiple VFCs to run concurrently, facilitating scalable and heterogeneous federated learning deployments.

## Getting started

To get started with the repository, follow these steps:

1. **Build the Project**

   ```sh
   make build
   ```

2. **Download the required Datasets**

   ```sh
   make download-datasets
   ```

3. **Specify kleint-gateway port and IP address**:

    modify the `config.js` file replacing `<node-ip>` with the actual IP of the node hosting the kleint-gatway and port with 13579:
    <pre lang="javascript">
    // /opt/FLAT/config.js

    const kleintGateway = "&lt;node-ip&gt;:13579";
    const scriptLoadDelay = 100; //ms
    </pre>
4. **Set Environment Variables**

   Configure the environment variables by editing the `.env` file according to your setup.

5. **Run the Entire Architecture (CEC + Flower)**

   ```sh
   make run
   ```

6. **Stop the Flower VPods + Aggregator**

   ```sh
   make stop
   ```

7. **Remove the Entire Architecture**

   ```sh
   make remove
   ```

8. **Display Help for Available Commands**

   ```sh
   make help
   ```

## Contributions

Contributions are welcome! Please follow these guidelines when contributing to the project:

- **Fork the Repository:** Start by forking the project to your own repository.
- **Create a Branch:** Work on your feature or fix in a dedicated branch.
- **Commit Changes:** Ensure that your commits are well-documented and follow the project's coding standards.
- **Submit a Pull Request:** Once your changes are complete, submit a pull request for review.
- **Follow the Code of Conduct:** Respect the community guidelines and collaborate constructively.

For any questions or further discussions, feel free to open an issue or contact the project maintainers.