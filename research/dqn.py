
import sys
sys.path.append('./agents/')
sys.path.append('./')

print(sys.path)

from common.DataLoader import MaterialLoader
from common.TransferMatrix import OpticalModeling
from common.Config import FilmConfig
from common.utils.FilmLoss import film_loss
from common import Checkpointer

from tf_agents.agents.dqn import dqn_agent
from tf_agents.policies import policy_saver
from tf_agents.drivers import dynamic_step_driver
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.policies import q_policy, random_py_policy
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.environments import tf_py_environment
from tf_agents.utils.common import *

from absl import logging
logging.set_verbosity(logging.ERROR)

import datetime

#from common.FilmEnvironment import FilmEnvironment 

import tensorflow as tf 
import numpy as np

from common.FilmEnvironment import FilmEnvironment
filmEnv = FilmEnvironment(config_path='Zn.ini', random_init=True, debug=True)
logtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

filmEnv = tf_py_environment.TFPyEnvironment(filmEnv)

num_iterations = 20000 # @param {type:"integer"}

initial_collect_steps = 1000  # @param {type:"integer"} 
collect_steps_per_iteration = 1  # @param {type:"integer"}
replay_buffer_max_length = 100000  # @param {type:"integer"}

batch_size = 64  # @param {type:"integer"}
learning_rate = 1e-3  # @param {type:"number"}
log_interval = 1  # @param {type:"integer"}
save_interval = 20 # @param {type:"integer"}

num_eval_episodes = 10  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}


fc_layer_params = (64, 128, 64)

q_net = q_network.QNetwork(
    filmEnv.observation_spec(),
    filmEnv.action_spec(),
    fc_layer_params=fc_layer_params)

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)
global_step = tf.compat.v1.train.get_or_create_global_step()

train_step_counter = tf.Variable(0)

agent = dqn_agent.DqnAgent(
    filmEnv.time_step_spec(),
    filmEnv.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=element_wise_squared_loss,
    train_step_counter=train_step_counter)

agent.initialize()

eval_policy = agent.policy
collect_policy = agent.collect_policy

replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=filmEnv.batch_size,
    max_length=replay_buffer_max_length)


checkpoint_dir = "./log/checkpoints/"
train_checkpointer = Checkpointer(
    ckpt_dir=checkpoint_dir,
    max_to_keep=1,
    agent=agent,
    policy=agent.policy,
    replay_buffer=replay_buffer,
    global_step=global_step
)

policy_dir = os.path.join("./log/checkpoints")
tf_policy_saver = policy_saver.PolicySaver(agent.policy)


def collect_step(environment, policy, buffer):
  time_step = environment.current_time_step()
  action_step = policy.action(time_step)
  next_time_step = environment.step(action_step.action)
  traj = trajectory.from_transition(time_step, action_step, next_time_step)

  # Add trajectory to the replay buffer
  buffer.add_batch(traj)

def collect_data(env, policy, buffer, steps):
  for _ in range(steps):
    collect_step(env, policy, buffer)

def compute_avg_return(environment, policy, num_episodes=10):

  total_return = 0.0
  for _ in range(num_episodes):

    time_step = environment.reset()
    episode_return = 0.0

    while not time_step.is_last():
      action_step = policy.action(time_step)
      time_step = environment.step(action_step.action)
      episode_return += time_step.reward
    total_return += episode_return

  avg_return = total_return / num_episodes
  return avg_return.numpy()[0]


dataset = replay_buffer.as_dataset(
    num_parallel_calls=3, 
    sample_batch_size=batch_size, 
    num_steps=2).prefetch(3)

iterator = iter(dataset)

avg_return = compute_avg_return(filmEnv, agent.policy, num_eval_episodes)
returns = [avg_return]

for _ in range(num_iterations):

  collect_data(filmEnv, agent.collect_policy, replay_buffer, batch_size)

  # Sample a batch of data from the buffer and update the agent's network.
  experience, _= next(iterator)
  train_loss = agent.train(experience).loss

  step = agent.train_step_counter.numpy()

  with open(f"./log/run_logs/run_{logtime}.txt", "a") as file:
    if step % log_interval == 0:
        print('step = {0}: loss = {1}'.format(step, train_loss))
        file.write('\n\n\nstep = {0}: loss = {1}\n'.format(step, train_loss))

        fileEnvInfo = filmEnv.get_info()
        aim = fileEnvInfo[0]
        weight = fileEnvInfo[1]
        observation = fileEnvInfo[2]
        composition = fileEnvInfo[3]
        loss_absorbation   = np.mean(weight['Absorption'] * (abs(aim['Absorption'] - observation[0])))
        loss_transimission = np.mean(weight['Transmission'] * (abs(aim['Transmission'] - observation[1])))
        loss_refraction    = np.mean(weight['Reflection'] * (abs(aim['Reflection'] - observation[2])))

        file.write(f"Composition: [{', '.join([str(float(list(i)[0])) for i in composition])}]\n")
        file.write(f'Postoptimisation state: [Absorption]{np.mean(observation[0])}, [Transmission]{np.mean(observation[1])}, [Reflection]{np.mean(observation[2])}\n')
        file.write(f"Ideal state: [Absorption]{np.mean(aim['Absorption'])}, [Transmission]{np.mean(aim['Transmission'])}, [Reflection]{np.mean(aim['Reflection'])}\n")
        file.write(f"film_loss: {np.sum([loss_absorbation, loss_transimission, loss_refraction])}\n")
        file.write(f"observation: {1 / np.sum([loss_absorbation, loss_transimission, loss_refraction])}\n")
        

        file.write('')
        file.close()

  if step % save_interval == 0:
    train_checkpointer.save(global_step)
    tf_policy_saver.save(policy_dir)
      
                                                           





