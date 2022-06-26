import torch
import torchvision

class ResNet18(torch.nn.Module):
    def __init__(self, output_features):
        super().__init__()
        self.model = torchvision.models.resnet18(pretrained=True)
        n_inputs = self.model.fc.in_features
        self.model.fc = torch.nn.Linear(n_inputs, output_features)
        
    def forward(self, x):
        return self.model(x)