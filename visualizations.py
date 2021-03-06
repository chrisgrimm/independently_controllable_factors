import cv2, numpy as np, os
from utils import horz_stack_images
from network import IndepFeatureLearner
from gridworld import SimpleGridworld

def get_all_states(env : SimpleGridworld):
    all_positions = [(y, x) for x in range(11) for y in range(11)]
    all_observations = [env.get_observation(pos) for pos in all_positions]
    return all_positions, all_observations

def visualize_correlation(file_path : str, network : IndepFeatureLearner, env : SimpleGridworld):
    all_positions, all_observations = get_all_states(env)
    all_fs = network.get_f(all_observations) # [bs, num_factors]
    images = []
    for i in range(network.num_factors):
        all_f_i = all_fs[:, i]
        canvas = np.zeros([11,11], dtype=np.float32)
        for pos, f in zip(all_positions, all_f_i):
            canvas[pos[0], pos[1]] = f
        canvas = (canvas + 1) / 2
        canvas = (255 * canvas).astype(np.uint8)
        canvas = cv2.applyColorMap(canvas, cv2.COLORMAP_JET)
        canvas = cv2.resize(canvas, (400, 400), interpolation=cv2.INTER_NEAREST)
        images.append(canvas)

    for i, image in enumerate(images):
        cv2.imwrite(file_path + f'correlation{i}.png', image)

def visualize_policies(file_path : str, network : IndepFeatureLearner, env : SimpleGridworld):
    all_positions, all_observations = get_all_states(env)
    all_pi = network.get_all_pi(all_observations)
    canvas = (255*np.transpose(np.mean(all_pi, axis=0), [1,0])).astype(np.uint8) #[num_actions, num_factors]
    canvas = cv2.applyColorMap(canvas, cv2.COLORMAP_JET)
    canvas = cv2.resize(canvas, (400, 400), interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(file_path + f'policy_averages.png', canvas)

def visualize_autoencoder(file_path : str, network : IndepFeatureLearner, env : SimpleGridworld):
    all_positions, all_observation = get_all_states(env)
    all_recons = network.get_recon(all_observation)
    print()
    for recon, position, obs in zip(all_recons, all_positions, all_observation):
        recon = 255*cv2.resize(recon, (400, 400), interpolation=cv2.INTER_NEAREST)
        recon = np.tile(np.reshape(recon, [400, 400, 1]), [1,1,3])
        orig = 255*cv2.resize(obs, (400, 400), interpolation=cv2.INTER_NEAREST)
        orig = np.tile(np.reshape(orig, [400, 400, 1]), [1,1,3])
        stacked = horz_stack_images(orig, recon, background_color=(255, 0, 0))
        cv2.imwrite(file_path+f'({position[1]}_{position[0]}.png', stacked)

