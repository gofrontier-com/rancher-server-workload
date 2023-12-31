import os
import shutil
from helpers.apply_terraform import apply_terraform
from helpers.download_kubeconfig import download_kubeconfig
from helpers.exec import exec
from helpers.get_bootstrap_password import get_bootstrap_password
from helpers.get_ingress_external_ip import get_ingress_external_ip
from tempfile import TemporaryDirectory


def deploy():
    region = os.getenv("REGION")

    terraform_output = apply_terraform(
        working_dir=os.path.join(os.getcwd(), "src/terraform/infra"),
        region=region,
        environment=os.getenv("ENVIRONMENT"),
        zone=os.getenv("ZONE"),
        set=os.getenv("SET"),
        workload_name="{0}-infra".format(os.getenv("WORKLOAD_NAME")),
        workload_type=os.getenv("WORKLOAD_TYPE"),
        workload_version=os.getenv("WORKLOAD_VERSION"),
        var_file=os.path.join(os.getcwd(), ".config", "main.tfvars"),
    )

    kubernetes_cluster_id = terraform_output["kubernetes_cluster_id"]["value"]
    key_vault_id = terraform_output["key_vault_id"]["value"]

    kubernetes_cluster_subscription_id = kubernetes_cluster_id.split("/")[2]
    kubernetes_cluster_resource_group_name = kubernetes_cluster_id.split(
        "/")[4]
    kubernetes_cluster_name = kubernetes_cluster_id.split("/")[8]

    temp_dir_path = TemporaryDirectory()
    kubeconfig_file_path = download_kubeconfig(
        dest_dir_path=temp_dir_path.name,
        client_id=os.getenv("ARM_CLIENT_ID"),
        client_secret=os.getenv("ARM_CLIENT_SECRET"),
        tenant_id=os.getenv("ARM_TENANT_ID"),
        cluster_subscription_id=kubernetes_cluster_subscription_id,
        cluster_resource_group_name=kubernetes_cluster_resource_group_name,
        cluster_name=kubernetes_cluster_name,
    )

    command = "helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx"
    exec(command=command, opts={"silent": False})

    command = "helm repo add jetstack https://charts.jetstack.io"
    exec(command=command, opts={"silent": False})

    command = "helm repo add rancher-stable https://releases.rancher.com/server-charts/stable"
    exec(command=command, opts={"silent": False})

    command = "helm repo update"
    exec(command=command, opts={"silent": False})

    command = "helm upgrade ingress-nginx ingress-nginx/ingress-nginx \
        --version 4.6.1 \
        --namespace ingress-nginx \
        --create-namespace \
        --install \
        --wait \
        --kubeconfig \"{0}\" \
        --set controller.service.annotations.\"service\\.beta\\.kubernetes\\.io/azure-load-balancer-health-probe-request-path\"=/healthz".format(kubeconfig_file_path)
    exec(command=command, opts={"silent": False})

    command = "helm upgrade cert-manager jetstack/cert-manager \
        --version v1.5.1 \
        --namespace cert-manager \
        --create-namespace \
        --install \
        --wait \
        --kubeconfig \"{0}\" \
        --set installCRDs=true".format(kubeconfig_file_path)
    exec(command=command, opts={"silent": False})

    ingress_external_ip = get_ingress_external_ip(kubeconfig_file_path)
    external_hostname = "{0}.nip.io".format(ingress_external_ip)

    command = "helm upgrade rancher rancher-stable/rancher \
        --version \"{0}\" \
        --namespace cattle-system \
        --create-namespace \
        --install \
        --wait \
        --kubeconfig \"{1}\" \
        --set global.cattle.psp.enabled=\"false\" \
        --set hostname=\"{2}\" \
        --set ingress.ingressClassName=\"nginx\" \
        --set replicas=\"{3}\"".format(
        os.getenv("RANCHER_VERSION"),
        kubeconfig_file_path,
        external_hostname,
        os.getenv("REPLICAS")
    )
    exec(command=command, opts={"silent": False})

    command = "kubectl rollout status deploy/rancher \
        --namespace cattle-system \
        --kubeconfig \"{0}\"".format(kubeconfig_file_path)
    exec(command=command, opts={"silent": False})

    bootstrap_password = get_bootstrap_password(kubeconfig_file_path)

    terraform_output = apply_terraform(
        working_dir=os.path.join(os.getcwd(), "src/terraform/config"),
        region=region,
        environment=os.getenv("ENVIRONMENT"),
        zone=os.getenv("ZONE"),
        set=os.getenv("SET"),
        workload_name="{0}-config".format(os.getenv("WORKLOAD_NAME")),
        workload_type=os.getenv("WORKLOAD_TYPE"),
        workload_version=os.getenv("WORKLOAD_VERSION"),
        vars={
            "bootstrap_password": bootstrap_password,
            "rancher_server_api_url": "https://{0}".format(external_hostname),
            "rancher_server_key_vault_id": key_vault_id,
        }
    )

    shutil.rmtree(temp_dir_path.name)


if __name__ == "__main__":
    deploy()
