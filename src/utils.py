import requests
import json
import sys
import logging
import argparse
import yaml


def parse_args(args):
    """
    Parses command line arguments based on a list of dictionaries
    :param args: The list of dictionaries defining command line args. Format:
    [
        {
            # 'definition' can be a:
            #   list containing the abbreviated and full names of an optional arg; ['-abrev_name', '--full_name']
            #   string name of an optional arg; '-abrev_name' OR '--full_name'
            #   string name of a required positional arg; 'full_name' ()
            'definition': ['-abrev_name', '--full_name'],
            # 'params' can be any parameters of argparse.ArgumentParser.add_argument().
            #   https://docs.python.org/3/library/argparse.html#the-add-argument-method
            'params': {
                'default': None, # default value
                'help': '<Your explanation of what this arg means and any other helpful documentation>'
                # ... more params
            }
        },
        {
            # ...another arg here
        }
    ]
    :return: dictionary of command line arg values
    """
    ap = argparse.ArgumentParser()
    for item in args:
        if isinstance(item['definition'], list):
            ap.add_argument(*item['definition'], **item['params'])
        else:
            ap.add_argument(item['definition'], **item['params'])
    return vars(ap.parse_args())


def parse_yaml(file_path):
    """
    Parses a yaml file
    :param file_path: Path of the yaml file to parse
    :return: The parsed yaml file
    """
    with open(file_path, 'r') as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as exc:
            sys.exit(exc)


def get_logger(name, stream=sys.stdout, style='{', frmt='{name} [{levelname}]:: {message}', level='INFO'):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler(stream=stream)
    formatter = logging.Formatter(frmt, style=style)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def api_get_request(url):
    response = requests.get(url)
    response.raise_for_status()
    response_text = json.loads(response.text)
    return response_text


def format_response(response, key_map):
    if isinstance(response, dict):
        formatted_response = _format_record(response, key_map)
    else:
        formatted_response = list()
        for record in response:
            formatted_record = _format_record(record, key_map)
            formatted_response.append(formatted_record)
    return formatted_response


def _format_record(record, key_map):
    formatted_record = dict()
    for k, v in key_map.items():
        if record.get(k):
            _format_key(record, k, v, formatted_record)
    return formatted_record


def _format_key(record, key, value, formatted_record):
    if isinstance((sub_record := record[key]), dict):
        for sub_key, sub_value in value.items():
            _format_key(sub_record, sub_key, sub_value, formatted_record)
    else:
        formatted_record[value or key] = record.get(key)
