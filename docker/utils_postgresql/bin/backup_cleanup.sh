#!/bin/bash

ls -dAct1 /backups/* | tail -n +2 | xargs rm -rf --
