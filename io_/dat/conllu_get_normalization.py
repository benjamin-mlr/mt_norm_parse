import re
from io_.info_print import printing


def get_normalized_token(norm_field, n_exception, verbose):
  match = re.match("^Norm=([^|]+)|.+", norm_field)
  try:
    assert match.group(1) is not None, " ERROR : not normalization found for norm_field {} ".format(norm_field)
  except:
    match_double_bar = re.match("^Norm=([|]+)|.+", norm_field)
    if match_double_bar.group(1) is not None:
      match = match_double_bar
      n_exception += 1
      printing("Exception handled we match with {}".format(match_double_bar.group(1)), verbose=verbose, verbose_level=2)
    else:
      print("Failed to handle exception with | ")
      raise (Exception)
  normalized_token = match.group(1)
  return normalized_token, n_exception
