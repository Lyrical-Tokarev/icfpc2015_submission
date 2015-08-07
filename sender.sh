#!/bin/bash

curl --user :bG1QPBtg8URhNEi7osmst019lroaf6HcAC1hXiROBeI= -X POST -H "Content-Type: application/json" \
        --data @$1 \
        https://davar.icfpcontest.org/teams/27/solutions
