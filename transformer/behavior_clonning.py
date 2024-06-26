import torch
import torch.nn as nn

class TrajectoryModel(nn.Module):

    def __init__(self, state_dim, act_dim, max_length=None):
        super().__init__()

        self.state_dim = state_dim
        self.act_dim = act_dim
        self.max_length = max_length

    def forward(self, states, actions, rewards, masks=None, attention_mask=None):
        # "masked" tokens or unspecified inputs can be passed in as None
        return None, None, None

    def get_action(self, states, actions, rewards, **kwargs):
        # these will come as tensors on the correct device
        return torch.zeros_like(actions[-1])



class MLBehaviorClonning(TrajectoryModel):
    """
    Simple MLP that predicts next action a from past states s.
    """
    def __init__(self, state_dim, act_dim, hidden_size, n_layer, dropout=0.1, max_length=1, **kwargs):
        super().__init__(state_dim, act_dim)

        self.hidden_size = hidden_size
        self.max_length = max_length
    
        layers = [nn.Linear(max_length*self.state_dim, hidden_size)]

        for _ in range(n_layer-1):
            layers.extend([
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_size, hidden_size)])
            
        layers.extend([
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, self.act_dim),
            nn.Tanh(),
        ])

        self.model = nn.Sequential(*layers)

    def forward(self,states: torch.Tensor, actions: torch.Tensor, rewards: torch.Tensor, attention_mask = None, target_return = None):

        states = states[:,-self.max_length:].reshape(states.shape[0], -1)  # concat states
        actions = self.model(states).reshape(states.shape[0], 1, self.act_dim)

        return None, actions, None
    
    def get_action(self, states: torch.Tensor, actions: torch.Tensor, rewards: torch.Tensor, **kwargs) -> torch.Tensor:

        states = states.reshape(1, -1, self.state_dim)
        if states.shape[1] < self.max_length:
            states = torch.cat([torch.zeros((1, self.max_length-states.shape[1], self.state_dim),
                             dtype=torch.float32, device=states.device), states], dim=1)
        states = states.to(dtype=torch.float32)
        _, actions, _ = self.forward(states, None, None, **kwargs)

        return actions[0,-1]


        

