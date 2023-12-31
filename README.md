# rancher-server-workload

[![CI](https://github.com/frontierdigital/rancher-server-workload/actions/workflows/ci.yml/badge.svg)](https://github.com/frontierdigital/rancher-server-workload/actions/workflows/ci.yml)

## About
Deploys [SUSE Rancher Server](https://www.suse.com/solutions/enterprise-container-management) on [Azure Kubernetes Service](https://azure.microsoft.com/en-gb/products/kubernetes-service), including integration into Microsoft Entra ID (Azure AD), Azure Monitor and Microsoft Defender for Cloud.

## Requirements
### Python
See the [.python-version](.python-version) file.

### Terraform
See the [.tfswitchrc](.tfswitchrc) file.

### Helm
See the [.helm-version](.helm-version) file.

## Test
```sh
INCLUDE_DEV=true make install
make test
```

## Configuration
```sh
# config/[environment]/env.properties

RANCHER_VERSION="[Rancher Server version, e.g. 2.7.4]"
REPLICAS="[Replica count, e.g. 2]"
```
```sh
# config/[environment]/main.tfvars

cidrsubnet_netnum  = "[CIDR subnet network number, e.g. 9]"
cidrsubnet_newbits = "[CIDR subnet network new bits, e.g. 12]"
kubernetes_version = "[kubernetes version, e.g. 1.25.11]"
node_count         = "[node count, e.g. 3]"
vm_size            = "[VM size, e.g. Standard_D2s_v3]"
```

## Deploy
```sh
export ARM_CLIENT_ID="[ARM client ID]" \
  ARM_CLIENT_SECRET="[ARM client secret]" \
  ARM_SUBSCRIPTION_ID="[ARM subscription ID]" \
  ARM_TENANT_ID="[ARM tenant ID]" \
  ENVIRONMENT="[environment]" \
  REGION="[region]" \
  SET="[set]" \
  WORKLOAD_NAME="[workload name]" \
  WORKLOAD_TYPE="rancher-cluster-workload" \
  WORKLOAD_VERSION="[workload version]" \
  ZONE="[zone]"
make deploy
```
