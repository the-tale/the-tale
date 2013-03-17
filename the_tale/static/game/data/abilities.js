
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.data) {
    pgf.game.data = {};
}

pgf.game.data.abilities = {
    
    
    "arenapvp1x1": {
        "type": "arenapvp1x1",
        "use_form": false,
        "name": "Отправить на арену",
        "description": "Отправить героя на гладиаторскую арену",
        "cost": 1
    },
    "buildingrepair": {
        "type": "buildingrepair",
        "use_form": false,
        "name": "Вызвать рабочего",
        "description": "Вызвать рабочего для ремонта здания",
        "cost": 3
    },
    "arenapvp1x1leavequeue": {
        "type": "arenapvp1x1leavequeue",
        "use_form": false,
        "name": "Выйти из очереди",
        "description": "Выйти из очереди на арену",
        "cost": 0
    },
    "help": {
        "type": "help",
        "use_form": false,
        "name": "Помочь",
        "description": "Попытаться помочь герою, чем бы тот не занимался",
        "cost": 4
    }
}