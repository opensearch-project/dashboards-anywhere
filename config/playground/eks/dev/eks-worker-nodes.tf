#
# EKS Worker Nodes Resources
#  * IAM role allowing Kubernetes actions to access other AWS services
#  * EKS Node Group to launch worker nodes
#

resource "aws_iam_role" "playground-dev-node" {
  name = "playground-dev-node"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "playground-dev-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.playground-dev-node.name
}

resource "aws_iam_role_policy_attachment" "playground-dev-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.playground-dev-node.name
}

resource "aws_iam_role_policy_attachment" "playground-dev-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.playground-dev-node.name
}

resource "aws_eks_node_group" "playground-dev" {
  cluster_name    = aws_eks_cluster.playground-dev.name
  node_group_name = "playground-dev"
  node_role_arn   = aws_iam_role.playground-dev-node.arn
  subnet_ids      = aws_subnet.playground-dev[*].id
  disk_size       = 300
  instance_types  = ["m5.2xlarge"]

  scaling_config {
    desired_size = 1
    max_size     = 3
    min_size     = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.playground-dev-node-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.playground-dev-node-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.playground-dev-node-AmazonEC2ContainerRegistryReadOnly,
  ]
}
