import torch
import torch.nn as nn


class ImagePixelPredictor(nn.Module):
    def __init__(self, n_input_channels: int, n_hidden_layers: int, n_hidden_kernels: int, n_output_channels: int):
        """CNN, consisting of "n_hidden_layers" linear layers, using relu
        activation function in the hidden CNN layers.

        Parameters
        ----------
        n_input_channels: int
            Number of features channels in input tensor
        n_hidden_layers: int
            Number of hidden layers
        n_hidden_kernels: int
            Number of kernels in each hidden layer
        n_output_channels: int
            Number of features in output tensor
        """
        super().__init__()

        hidden_layers = []
        for _ in range(n_hidden_layers):
            # Add a CNN layer
            layer = nn.Conv2d(in_channels=n_input_channels,
                              out_channels=n_hidden_kernels,
                              kernel_size=(3, 3),
                              padding="same")

            hidden_layers.append(layer)
            # Add relu activation module to list of modules
            hidden_layers.append(nn.ReLU())
            n_input_channels = n_hidden_kernels

        self.hidden_layers = nn.Sequential(*hidden_layers)
        self.output_layer = nn.Conv2d(in_channels=n_input_channels,
                                      out_channels=n_output_channels,
                                      kernel_size=(3, 3),
                                      padding="same")

    def forward(self, input_arr: torch.Tensor, known_arr: torch.Tensor):
        """Apply CNN to "x"

        Parameters
        ----------
        input_arr: torch.Tensor
            Input tensor of shape (n_samples, n_input_channels, x, y)

        known_arr: torch.Tensor
            Known tensor of shape (n_samples, n_input_channels, x, y)

        Returns
        ----------
        torch.Tensor
            Output tensor of shape (n_samples, n_output_channels, u, v)
        """
        # Concatenate input_array and known_array
        x = torch.concat((input_arr, known_arr), 1)

        # Apply hidden layers module
        hidden_features = self.hidden_layers(x)

        # Apply last layer (=output layer)
        x = self.output_layer(hidden_features)
        x = torch.clamp(x, 0, 255)
        return x
