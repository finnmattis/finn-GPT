#!/bin/bash

sudo rm -r dist
npm run build
firebase deploy