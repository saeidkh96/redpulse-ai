terraform {
  required_version = ">= 1.6.0"
}

variable "location" {
  type    = string
  default = "westeurope"
}

# Reference scaffold only. Live Azure resources should be added after
# credentials, tenancy, networking, cost, and deployment requirements are validated.
