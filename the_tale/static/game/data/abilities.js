
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
        "name": "Отправить на арену",
        "description": "Отправить героя на гладиаторскую арену",
        "cost": 1
    },
    "buildingrepair": {
        "type": "buildingrepair",
        "name": "Вызвать рабочего",
        "description": "Вызвать рабочего для ремонта здания",
        "cost": 3
    },
    "arenapvp1x1leavequeue": {
        "type": "arenapvp1x1leavequeue",
        "name": "Выйти из очереди",
        "description": "Выйти из очереди на арену",
        "cost": 0
    },
    "help": {
        "type": "help",
        "name": "Помочь",
        "description": "Попытаться помочь герою, чем бы тот не занимался",
        "cost": 4
    },
    "arenapvp1x1accept": {
        "type": "arenapvp1x1accept",
        "name": "Принять вызов",
        "description": "Принять вызов другого героя",
        "cost": 1
    }
}