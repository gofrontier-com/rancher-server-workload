# module "kubernetes_service" {
#   source = "git::https://github.com/frontierdigital/kubernetes-service-terraform-module//src?ref=v1.0.0-pre.c7998e3"

#   environment                = var.environment
#   identifier                 = local.identifier
#   kubernetes_version         = var.kubernetes_version
#   location                   = var.location
#   log_analytics_workspace_id = data.azurerm_log_analytics_workspace.main.id
#   node_count                 = var.node_count
#   resource_group_name        = module.resource_group.name
#   subnet_id                  = azurerm_subnet.main.id
#   workload_name              = var.workload_name
#   workload_type              = var.workload_type
#   workload_version           = var.workload_version
#   zone                       = var.zone
# }