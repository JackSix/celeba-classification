#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 15:10:00 2018

@author: Yacalis
"""

import os
import json
import numpy as np
from Callbacks import Callbacks
from Config import Config
from dataLoader import retrieve_data, retrieve_celeba_data
from folder_defs import get_log_dir, get_data_dir, get_train_dir, get_test_dir, get_celeba_dir
from build_model import build_model
from save_model import save_model
from get_data_dict import get_data_dict, get_new_data_dict, get_celeba_data
from sklearn.model_selection import train_test_split

def main():
    print('Beginning program')

    # get config
    config = Config().config
    print('change lr:', config.change_lr)
    print('change bs:', config.change_bs)
    print('max epochs:', config.epochs)
    if config.change_bs and config.change_lr:
        print('[!] Whoops: both config.change_bs and config.change_lr are '
              'true -- at least one of them should be false.')
        return

    # get directories
    log_dir = get_log_dir(config)
    data_dir = get_data_dir()
    #train_dir = get_train_dir()
    #test_dir = get_test_dir()
    image_dir = get_celeba_dir()
    print('log dir:', log_dir)
    print('data dir:', data_dir)
    #print('train dir:', train_dir)
    #print('test dir:', test_dir)
    print('image_dir:', image_dir)

    # get data
    print('Loading data...')
    data_dict = get_celeba_data(data_dir)
    x_data, y_data = retrieve_celeba_data(data_dict=data_dict, image_dir=image_dir)
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, shuffle=True)
    num_train = int(x_train.shape[0] * 0.8)
    print(f'Num training examples (excludes test and val): {num_train}')

    # build and save initial model
    input_dim = x_train[0].shape
    model = build_model(input_dim, config, model_type=config.complexity)
    save_model(log_dir=log_dir, config=config, model=model)

    # set variables
    val_loss = []
    val_acc = []
    loss = []
    acc = []
    lr = []
    bs = []
    max_epochs = config.epochs
    batch_size = config.batch_size
    batch_size_mult = 2
    epoch_iter = 1

    # get callbacks
    callbacks = Callbacks(config, log_dir).callbacks
    print('callbacks:')
    for callback in callbacks:
        print('\t', callback)

    # train model
    if config.change_lr:  # reduce_lr callback takes care of everything for us
        print('Will change learning rate during training, but not batch size')
        print('Training model...')
        history = model.fit(x_data,
                            y_data,
                            epochs=max_epochs,
                            batch_size=batch_size,
                            shuffle=True,
                            validation_split=0.2,
                            verbose=1,
                            callbacks=callbacks)
        # store history (bs is constant)
        val_loss += history.history['val_loss']
        val_acc += history.history['val_acc']
        loss += history.history['loss']
        acc += history.history['acc']
        lr += history.history['lr']
        bs = [batch_size for i in range(len(history.epoch))]

    elif config.change_bs:  # need to manually stop and restart training
        print('Will change batch size during training, but not learning rate')
        while max_epochs >= epoch_iter:
            print(f'Currently at epoch {epoch_iter} of {max_epochs}, batch size is {batch_size}')
            epochs = max_epochs - epoch_iter + 1
            history = model.fit(x_data,
                                y_data,
                                epochs=epochs,
                                batch_size=batch_size,
                                shuffle=True,
                                validation_split=0.2,
                                verbose=1,
                                callbacks=callbacks)
            # store history
            val_loss += history.history['val_loss']
            val_acc += history.history['val_acc']
            loss += history.history['loss']
            acc += history.history['acc']
            bs += [batch_size for i in range(len(history.epoch))]

            # update training parameters
            epoch_iter += len(history.epoch)
            batch_size *= batch_size_mult
            batch_size = batch_size if batch_size < num_train else num_train

        # store lr history as constant (because it is)
        lr = [0.001 for i in range(len(bs))]

    else:
        print('Will not change learning rate nor batch size during training')
        print('Training model...')
        history = model.fit(x_data,
                            y_data,
                            epochs=max_epochs,
                            batch_size=batch_size,
                            shuffle=True,
                            validation_split=0.2,
                            verbose=1,
                            callbacks=callbacks)
        # store history (bs is constant)
        val_loss += history.history['val_loss']
        val_acc += history.history['val_acc']
        loss += history.history['loss']
        acc += history.history['acc']
        lr = [0.001 for i in range(len(history.epoch))]
        bs = [batch_size for i in range(len(history.epoch))]

    print('Completed training')

    # save finished model -- overrides original model saved before training
    save_model(log_dir=log_dir, config=config, model=model)

    # save loss, accuracy, lr, and bs values across epochs as json;
    # have to force cast lr vals as float64 because history object saves them
    # as float32, and json.dump() is not compatible with float32
    acc_loss_lr_bs = {'val_loss': val_loss,
                      'val_acc': val_acc,
                      'loss': loss,
                      'acc': acc,
                      'lr': [np.float64(i) for i in lr],
                      'bs': bs
                      }
    acc_loss_lr_bs_path = os.path.join(log_dir, 'acc_loss_lr_bs.json')
    with open(acc_loss_lr_bs_path, 'w') as f:
        json.dump(acc_loss_lr_bs, f, indent=4, sort_keys=True)

    # evaluate model (on original batch size)
    print('Calculating final score...')
    #x_data, y_data = retrieve_data(data_dict=data_dict, image_dir=test_dir)
    score = model.evaluate(x_test, y_test, batch_size=config.batch_size)
    print('Final score:', score)

    print('Completed program')

    return


if __name__ == '__main__':
    main()
