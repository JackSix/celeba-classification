#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 15:21:00 2018

@author: Yacalis
"""

import os
import json
import configargparse


class Config:
    def __init__(self):
        self.config, unparsed = self.main()
        if unparsed:
            raise Exception(f'[!] Something is wrong - there are unrecognized \
                            parameters present: {unparsed}')
        return

    @staticmethod
    def main() -> (object, object):
        parser = configargparse.ArgParser()

        # Callbacks
        cback_arg = parser.add_argument_group('Callbacks')
        # Earlystopping
        cback_arg.add_argument('--es_min_delta', type=float, default=0.00001)
        cback_arg.add_argument('--es_patience', type=int, default=10)
        # ReduceLROnPlateau
        cback_arg.add_argument('--lr_epsilon', type=float, default=1e-04)
        cback_arg.add_argument('--lr_factor', type=float, default=0.1)
        cback_arg.add_argument('--lr_min_lr', type=float, default=1e-07)
        cback_arg.add_argument('--lr_patience', type=int, default=5)
        # Model Checkpoint
        cback_arg.add_argument('--period', type=int, default=10)

        # Data
        data_arg = parser.add_argument_group('Data')
        data_arg.add_argument('--input_vars', type=str, default='')
        data_arg.add_argument('--output_vars', type=str, default='')

        # Misc
        misc_arg = parser.add_argument_group('Misc')
        misc_arg.add_argument('--random_seed', type=int, default=123)

        # Training and testing
        train_arg = parser.add_argument_group('Training')
        train_arg.add_argument('--batch_size', type=int, default=50)
        train_arg.add_argument('--epochs', type=int, default=200)
        train_arg.add_argument('--shuffle', type=bool, default=True)
        train_arg.add_argument('--change_lr', type=bool, default=True)
        train_arg.add_argument('--change_bs', type=bool, default=False)

        return parser.parse_known_args()

    @staticmethod
    def save_config(config: object, logdir: str) -> None:
        param_path = os.path.join(logdir, 'params.json')
        with open(param_path, 'w') as f:
            json.dump(config.__dict__, f, indent=4, sort_keys=True)