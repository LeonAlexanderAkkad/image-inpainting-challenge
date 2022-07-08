import numpy as np
from PIL import Image
import os
import random
import dill as pkl
from helper_methods import ex4
from typing import Tuple
from tqdm import tqdm

from torchvision import transforms
from torchvision.transforms import InterpolationMode
from torch.utils.data import Dataset, Subset
import glob


class ImageDataset(Dataset):
    def __init__(self, path: str):
        if not os.path.exists("images_processed.pkl"):
            self.__process_dataset(path)

        with open("images_processed.pkl", "rb") as f:
            all_arrays = pkl.load(f)

        self.image_arrays = all_arrays["image_arrays"]
        self.known_arrays = all_arrays["known_arrays"]
        self.input_arrays = all_arrays["input_arrays"]

    def __getitem__(self, index):
        return self.image_arrays[index], self.input_arrays[index], self.known_arrays[index]

    def __len__(self):
        return len(self.input_arrays)

    ####################################################
    # Helper Methods
    ####################################################

    # noinspection PyMethodMayBeStatic
    def __process_dataset(self, file_path: str):
        content = glob.glob(os.path.join(file_path, '**', '*.jpg'), recursive=True)
        content.sort()
        resize = transforms.Compose([
            transforms.Resize((100, 100), interpolation=InterpolationMode.BILINEAR)
        ])
        random.seed(69)
        all_images = {}
        image_arrays, known_arrays, input_arrays = [], [], []

        for picture in tqdm(content, desc="Processing images"):
            with Image.open(picture) as image:
                image = resize(image)
            image_np = np.array(image)
            offset_0 = random.randint(0, 8)
            offset_1 = random.randint(0, 8)
            spacing_0 = random.randint(2, 6)
            spacing_1 = random.randint(2, 6)
            input_array, known_array, image_array = ex4(image_np, (offset_0, offset_1), (spacing_0, spacing_1))
            input_arrays.append(image_array)
            known_arrays.append(known_array)
            image_arrays.append(image_array)

        all_images["input_arrays"] = input_arrays
        all_images["known_arrays"] = known_arrays
        all_images["image_arrays"] = image_arrays

        with open("images_processed.pkl", "wb") as f:
            pkl.dump(all_images, f)

        print(f"Processed {len(content)} files")

    def split(self, ratios: Tuple[int, int, int], random_seed=69) -> Tuple[Subset, Subset, Subset]:
        ratios_sum = sum(ratios)

        n_samples = len(self)

        test_set_start = int(n_samples / ratios_sum) * ratios[0]
        validation_set_start = int(n_samples / ratios_sum) * (ratios[0] + ratios[1])

        shuffled_indices = np.random.default_rng(random_seed).permutation(n_samples)

        training_set_indices = shuffled_indices[:test_set_start]
        test_set_indices = shuffled_indices[test_set_start:validation_set_start]
        validation_set_indices = shuffled_indices[validation_set_start:]

        indices = {"training_set_indices": training_set_indices,
                   "test_set_indices": test_set_indices,
                   "validation_set_indices": validation_set_indices
                   }

        print(f'Splitting dataset into subsets with size '
              f'{len(training_set_indices)}, {len(test_set_indices)}, {len(validation_set_indices)}')

        with open("indices.pkl" "wb") as f:
            pkl.dump(indices, f)

        return (
            Subset(self, indices=training_set_indices),
            Subset(self, indices=test_set_indices),
            Subset(self, indices=validation_set_indices)
        )
