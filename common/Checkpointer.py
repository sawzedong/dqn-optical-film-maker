import numpy as np
import tensorflow as tf
from absl import logging

logging.set_verbosity(logging.ERROR)

class Checkpointer(object):
  """Checkpoints training state, policy state, and replay_buffer state."""

  def __init__(self, ckpt_dir, max_to_keep=20, **kwargs):
    """A class for making checkpoints.

    If ckpt_dir doesn't exists it creates it.

    Args:
      ckpt_dir: The directory to save checkpoints.
      max_to_keep: Maximum number of checkpoints to keep (if greater than the
        max are saved, the oldest checkpoints are deleted).
      **kwargs: Items to include in the checkpoint.
    """
    self._checkpoint = tf.train.Checkpoint(**kwargs)

    if not tf.io.gfile.exists(ckpt_dir):
      tf.io.gfile.makedirs(ckpt_dir)

    self._manager = tf.train.CheckpointManager(
        self._checkpoint, directory=ckpt_dir, max_to_keep=max_to_keep)

    if self._manager.latest_checkpoint is not None:
      logging.info('Checkpoint available: %s', self._manager.latest_checkpoint)
      self._checkpoint_exists = True
    else:
      logging.info('No checkpoint available at %s', ckpt_dir)
      self._checkpoint_exists = False
    self._load_status = self._checkpoint.restore(
        self._manager.latest_checkpoint)

  @property
  def checkpoint_exists(self):
    return self._checkpoint_exists

  @property
  def manager(self):
    """Returns the underlying tf.train.CheckpointManager."""
    return self._manager

  def initialize_or_restore(self, session=None):
    """Initialize or restore graph (based on checkpoint if exists)."""
    self._load_status.initialize_or_restore(session)
    return self._load_status

  def save(self, global_step: tf.Tensor,
           options: tf.train.CheckpointOptions = None):
    """Save state to checkpoint."""
    saved_checkpoint = self._manager.save(
        checkpoint_number=global_step, options=options)
    self._checkpoint_exists = True
    logging.info('%s', 'Saved checkpoint: {}'.format(saved_checkpoint))