def readnumber(data):
    data=data
    length = len(data)
    son = []
    for i in range(length):
        son.append(int(data[i]))
    ret = ''
    bir = ['', 'bir ', 'ikki ', 'uch ', "to'rt ", 'besh ', 'olti ', 'yetti ', 'sakkiz ', "to'qqiz "]
    on = ["", "o'n ", "yigirma ", "o'ttiz ", "qirq ", "ellik ", "oltmish ", "yetmish ", "sakson ", "to'qson "]
    yuz = ["", "bir yuz ", "ikki yuz ", "uch yuz ", "to'rt yuz ", "besh yuz ", "olti yuz ", "yetti yuz ", "sakkiz yuz ",
           "to'qqiz yuz "]
    if length == 1:
        ret = ret + bir[son[0]]
    elif length == 2:
        ret = ret + on[son[0]] + bir[son[1]]
    elif length == 3:
        ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]]
    elif length == 4:
        ret = ret + bir[son[0]] + 'ming ' + yuz[son[1]] + on[son[2]] + bir[son[3]]
    elif length == 5:
        ret = ret + on[son[0]] + bir[son[1]] + 'ming ' + yuz[son[2]] + on[son[3]] + bir[son[4]]
    elif length == 6:
        ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'ming ' + yuz[son[3]] + on[son[4]] + bir[son[5]]
    elif length == 7:
        if son[1] == 0 and son[2] == 0 and son[3] == 0:
            ret = ret + bir[son[0]] + 'million ' + yuz[son[4]] + on[
                son[5]] + bir[son[6]]
        else:
            ret = ret + bir[son[0]] + 'million ' + yuz[son[1]] + on[son[2]] + bir[son[3]] + 'ming ' + yuz[son[4]] + on[
                son[5]] + bir[son[6]]
    elif length == 8:
        if son[2] == 0 and son[3] == 0 and son[4] == 0:
            ret = ret + on[son[0]] + bir[son[1]] + 'million ' + yuz[
                son[5]] + on[son[6]] + bir[son[7]]
        else:
            ret = ret + on[son[0]] + bir[son[1]] + 'million ' + yuz[son[2]] + on[son[3]] + bir[son[4]] + 'ming ' + yuz[
                son[5]] + on[son[6]] + bir[son[7]]
    elif length == 9:
        if son[3] == 0 and son[4] == 0 and son[5] == 0:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'million ' + yuz[son[6]] + on[son[7]] + bir[son[8]]
        else:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'million ' + yuz[son[3]] + on[son[4]] + bir[
                son[5]] + 'ming ' + yuz[son[6]] + on[son[7]] + bir[son[8]]
    elif length == 10:
        if son[1] == 0 and son[2] == 0 and son[3] == 0 and son[4] == 0 and son[5] == 0 and son[6] == 0:
            ret = ret + bir[son[0]] + 'milliard ' + yuz[son[7]] + on[son[8]] + bir[son[9]]
        elif son[4] == 0 and son[5] == 0 and son[6] == 0:
            ret = ret + bir[son[0]] + 'milliard ' + yuz[son[1]] + on[son[2]] + bir[son[3]] + yuz[son[7]] + on[son[8]] + \
                  bir[son[9]]
        elif son[1] == 0 and son[2] == 0 and son[3] == 0:
            ret = ret + bir[son[0]] + 'milliard ' + yuz[son[4]] + on[
                son[5]] + bir[son[6]] + 'ming ' + yuz[son[7]] + on[son[8]] + bir[son[9]]
        else:
            ret = ret + bir[son[0]] + 'milliard ' + yuz[son[1]] + on[son[2]] + bir[son[3]] + 'million ' + yuz[son[4]] + \
                  on[son[5]] + bir[son[6]] + 'ming ' + yuz[son[7]] + on[son[8]] + bir[son[9]]
    elif length == 11:
        if son[2] == 0 and son[3] == 0 and son[4] and son[5] == 0 and son[6] == 0 and son[7]:
            ret = ret + on[son[0]] + bir[son[1]] + 'milliard ' + yuz[son[8]] + on[son[9]] + bir[son[10]]
        elif son[5] == 0 and son[6] == 0 and son[7] == 0:
            ret = ret + on[son[0]] + bir[son[1]] + 'milliard ' + yuz[son[2]] + on[son[3]] + bir[son[4]] + 'million ' + \
                  yuz[son[8]] + on[son[9]] + bir[son[10]]
        elif son[2] == 0 and son[3] == 0 and son[4] == 0:
            ret = ret + on[son[0]] + bir[son[1]] + 'milliard ' + yuz[
                son[5]] + on[son[6]] + bir[son[7]] + 'ming ' + yuz[son[8]] + on[son[9]] + bir[son[10]]
        else:
            ret = ret + on[son[0]] + bir[son[1]] + 'milliard ' + yuz[son[2]] + on[son[3]] + bir[son[4]] + 'million ' + \
                  yuz[
                      son[5]] + on[son[6]] + bir[son[7]] + 'ming ' + yuz[son[8]] + on[son[9]] + bir[son[10]]
    elif length == 12:
        if son[3] == 0 and son[4] == 0 and son[5] == 0 and son[6] == 0 and son[7] == 0 and son[8]:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + yuz[son[9]] + on[son[10]] + bir[
                son[11]]
        elif son[6] == 0 and son[7] == 0 and son[8] == 0:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'milliard ' + yuz[son[3]] + on[son[4]] + bir[
                son[5]] + 'million ' + yuz[son[9]] + on[son[10]] + bir[son[11]]
        elif son[3] == 0 and son[4] == 0 and son[5]:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'milliard ' + yuz[son[6]] + on[son[7]] + bir[
                son[8]] + 'ming ' + yuz[son[9]] + on[son[10]] + bir[son[11]]
        else:
            ret = ret + yuz[son[0]] + on[son[1]] + bir[son[2]] + 'milliard ' + yuz[son[3]] + on[son[4]] + bir[
                son[5]] + 'million ' + yuz[son[6]] + on[son[7]] + bir[son[8]] + 'ming ' + yuz[son[9]] + on[son[10]] + \
                  bir[
                      son[11]]
    return ret
