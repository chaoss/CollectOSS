#SPDX-License-Identifier: MIT
import pandas as pd
import os
# end imports
# (don't remove the above line, it's for a script)

def makeRelative(function):
  """
  Decorator that makes a timeseries relative to another timeseries
  """
  def generated_function(owner, repo, ownerRelativeTo, repoRelativeTo):
      baseData = function(ownerRelativeTo, repoRelativeTo)
      comparableData = function(owner, repo)
      columns = list(baseData.columns)
      columns.remove('date')
      relativeData = (
        pd
          .merge(baseData, comparableData, on='date', how='left')
          .dropna()
      )
      for col in columns:
        relativeData[col + '_ratio'] = relativeData[col + '_y'] / relativeData[col + '_x']
      return relativeData
  generated_function.__name__ = function.__name__ + '_relative'
  return generated_function

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)