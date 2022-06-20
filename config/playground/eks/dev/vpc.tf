#
# VPC Resources
#  * VPC
#  * Subnets
#  * Internet Gateway
#  * Route Table
#

resource "aws_vpc" "playground-dev" {
  cidr_block = "10.0.0.0/16"

  tags = tomap({
    "Name"                                      = "playground-dev-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_subnet" "playground-dev" {
  count = 2

  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.playground-dev.id

  tags = tomap({
    "Name"                                      = "playground-dev-node",
    "kubernetes.io/cluster/${var.cluster-name}" = "shared",
  })
}

resource "aws_internet_gateway" "playground-dev" {
  vpc_id = aws_vpc.playground-dev.id

  tags = {
    Name = "playground-dev"
  }
}

resource "aws_route_table" "playground-dev" {
  vpc_id = aws_vpc.playground-dev.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.playground-dev.id
  }
}

resource "aws_route_table_association" "playground-dev" {
  count = 2

  subnet_id      = aws_subnet.playground-dev.*.id[count.index]
  route_table_id = aws_route_table.playground-dev.id
}
