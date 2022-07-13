#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import csv 
import sys
# CGIモジュールをインポート
import cgi
import cgitb
from tokenize import Name
cgitb.enable()

#リストの作成
math = [] #単語の番号を入れるリスト
word = [] #英単語を入れるリスト
japanese = [] #日本語を入れるリスト
option = [1,2,3,4]
count = [1,1]
save = ["math","English","Japanese","number"] #回答を保存するためのリスト
renew_save = ["count","math","English","Japanese","number"] #更新ボタンを押しても問題ないようにするため、count[0] = 5になったときに使うcount[0] = 4の時の回答を保存するリスト
yet = [] #未回答リスト
yet_japanese  = [] #未回答または間違えた問題の、日本語リスト
mistake = [] #間違えた問題リスト


#リストの要素の何番目かを返す関数
def my_index(l,x,default = False):
    return l.index(x) if x in l else default 
    
#csvファイルを開き、1,2,3列目をそれぞれ、リスト math(番号を入れる) , 
# word(英単語を入れる) , japanese(日本語を入れる) へ
#また、未回答リスト yet も作成
with open('英単語2.csv', 'r', encoding='UTF-8') as file:
    data = []
    reader = csv.reader(file)
    for row in reader:
        data.append(row)
n = len(data)
for a in range(0,n):
    yet.append([data[a][0],data[a][1],data[a][2]])
    for b in range(0,3):
        if b==0:
            math.append(data[a][b])
        if b==1:
            word.append(data[a][b])
        if b==2:
            japanese.append(data[a][b])
            yet_japanese.append(data[a][b])

         
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
dbname = 'word.db'
#dbname = ':memory:'

# テーブルの作成

with open('英単語2.csv', 'r', encoding='UTF-8') as file:
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master"
          "    WHERE TYPE = 'table' AND name = 'English_Words'")
    row = cur.fetchone() # SQL文の実行結果をtupleで得る

    if row[0] == 1: # 1なら表が存在する, 結果はtupleなので最初の要素（0番目）を参照する
        print("表 English_Words は存在します")
    
    #表がなかった場合に表を作成する。 挿入により作成している
    else:
        print("表 English_Words を作成します")    
        create_table = 'create table if not exists English_Words (number int, word varchar(64), japanese varchar(64))'
        cur.execute(create_table)
        con.commit()
        for i in range(0,n):
            v1 = math[i]
            v2 = word[i]
            v3 = japanese[i]
            sql = 'insert into English_Words (number, word, japanese) values (?,?,?)'
            cur.execute(sql, (v1,v2,v3))
        con.commit()

    cur.close()
    con.close()




def application(environ,start_response):
    html = ""
    f = open('home.html', 'r', encoding="utf-8")
    f_in = open('input.html', 'r', encoding="utf-8")
    
    # HTML（共通ヘッダ部分）
    while (True):
        line = f.readline()
        if line == "":
            break
        html += line

    #正解番号の選択
    op = random.choice(option)
    #問題の日本語選択
    japan = random.choice(yet_japanese)
    save_number = yet_japanese.index(japan)
    number = japanese.index(japan)
    
    #a,b,c,d に間違い回答入れる
    save_math = math[number]
    save_word = word[number]
    word.pop(number)
    opa = random.choice(word)
    opb = random.choice(word)
    opc = random.choice(word)
    opd = random.choice(word)

    #a,b,c,dのいずれかに正当を入れる
    if op == 1:
        opa = save_word
    elif op == 2:
        opb = save_word
    elif op == 3:
        opc = save_word
    elif op == 4:
        opd = save_word                        
    word.insert(number,save_word)
    count[0] += 1
    
    #count[0] = 5になった場合に使う
    if count[0] == 4:
        renew_save[0] = op
        renew_save[1] = save_math
        renew_save[2] = save_word
        renew_save[3] = japan
        renew_save[4] = save_number

    #更新ボタンを押しちゃうと、その時だけおかしくなる。
    print(count,op)
    #答えの値等を保存しておく
    if count[0] % 4 ==2:
        print("OK")
        count[1] = op
        save[0] = save_math
        save[1] = save_word
        save[2] = japan
        save[3] = save_number
    
    #更新ボタンを押してもおかしくならないように（ただし、2回以上更新ボタン押されると困る）
    if count[0] == 5:
        count[1] = renew_save[0]
        save[0] = renew_save[1]
        save[1] = renew_save[2]
        save[2] = renew_save[3]
        save[3] = renew_save[4]
        count[0] = 3
        print(count)

    #置き換えデータの作成    
    page_data = {}
    page_data['japan'] = japan
    page_data['op_1'] = opa
    page_data['op_2'] = opb
    page_data['op_3'] = opc    
    page_data['op_4'] = opd

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form):
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

        # HTML（入力フォーム部分）

        while (True):
            line = f_in.readline()
            if line == "":
                break
            for key, value in page_data.items():
                html = html.replace('{% ' + key + ' %}', value)
            html += line

    else:

        # フォームデータから各フィールド値を取得
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        v3 = form.getvalue("v3","0")
        search = form.getvalue("search","0")
        add = form.getvalue("add","0")
        dele = form.getvalue("dele","0")
        wordall = form.getvalue("wordall","0")
        a = form.getvalue("a","0")
        b = form.getvalue("b","0")
        c = form.getvalue("c","0")
        d = form.getvalue("d","0")
        unknown = form.getvalue("unknown","0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        #表から検索するときに使用する関数exam
        def exam(sq,li):
            for row in cur.execute(*sq):
                li.append(row[0])
                li.append(row[1])
                li.append(row[2])
            return li 

        #検索結果を表示するのに使用する関数show
        def show(li):
            line = []
            num = (len(li))/3
            for i in range(int(num)):                        
                line.append(str(li[3*i]) + ' , ' + li[3*i+1] + ' , ' + li[3*i+2])
            return [line,num]

        #検索、追加、削除の条件分岐 

        #リスト作成
        listall = []
        listname = []
        listid = []

  

        numyet = my_index(yet,[save[0],save[1],save[2]],-1) #未回答問題リストの何番目にあるかを取得
        miss_number = my_index(mistake,[save[0],save[1],save[2]],-1) #間違えた問題リストの何番目にあるかを取得

        #問題

        #正しい回答を選んだ場合
        if count[1] == int(a) or count[1] == int(b) or count[1] == int(c) or count[1] == int(d):
            html += '<head>\n' \
                    '<br><p class = "mb3"><circle></circle>\n</p>' \
                    '<meta http-equiv="refresh" content="0.3;URL=http://localhost:50305/">\n' \
                    '</head>\n'                    
            yet_japanese.pop(save[3])
            if numyet != -1:       
                yet.pop(numyet)
            if miss_number != -1:
                mistake.pop(miss_number)
              
        #不正解または覚えていないボタンを押した場合
        elif int(a) + int(b) + int(c) + int(d) != 0 or unknown != "0":    
            html += '<p class = "mb4"><head></p>\n' \
                    '<p><div class = "cross"></div></p>\n' \
                    '<div class = "answer">' + save[2] + ' ⇆ ' + save[1] + '</div>\n<br>' \
                    '<meta http-equiv="refresh" content="5;URL=http://localhost:50305/">\n' \
                    '</head>\n'
            if numyet != -1:
                mistake.append(yet[numyet]) 
                yet.pop(numyet)

        #検索(単語すべてから検索している)
        elif search != "0":

        # SQL文（select）の作成

            #sql = 'select * from users'
            sqa = 'select * from English_Words where word like ? ' ,('%' +v2+ '%', )
            sql = 'select * from English_Words where japanese like ? ' ,('%' +v3+ '%', )
            sqall = 'select * from English_Words where japanese like ? and word like ?' ,('%' +v3+ '%', '%' +v2+ '%', )
            
            # SQL文の実行とその結果のHTML形式への変換
            html += '<body>\n' \
                    '<div class="ol1">\n' \


            #部分一致していたものをリストの中へ
            exam(sqall,listall)
            exam(sqa,listname)
            exam(sql,listid)            

            #word japanese どちらも部分一致あれば、表示、無ければ word の部分一致表示、
            #それもなければ、japanese の部分一致表示
            if len(listall) != 0:
                all_list = show(listall)
                for i in range(int(all_list[1])):
                    html += '<li>' + all_list[0][i] + '</li>\n'

            elif len(listid) !=0:
                word_list = show(listid)
                for i in range(int(word_list[1])):
                    html += '<li>' + word[0][i] + '</li>\n'

            elif len(listname) !=0:
                japan_list = show(listname)
                for i in range(int(japan_list[1])):
                    html += '<li>' + japan_list[0][i] + '</li>\n'
  
            html += '</div>\n' \
        #検索ここまで

                        
        #追加
        elif add != "0":

            # SQL文（insert）の作成と実行
            sql = 'insert into English_Words (number, word, japanese) values (?,?,?)'
            cur.execute(sql, (v1,v2,v3))
            con.commit()   
            #表示内容

            html += '<body>\n' \
                    '<div class="ol1">\n'   \
                    '<li>' + str(v1) + ',' + v2 + ',' + v3 + '</li>\n'\
                    '</div>\n' \
                    'これを追加しました。<br>\n' \
        #追加ここまで


        #削除            
        elif dele != "0":
        
            #DELETE文(消去)の作成
            sqall = 'select * from English_Words where number = ? and word = ? and japanese = ?' ,(v1,v2,v3, )

            #表示内容

            html += '<body>\n' \
                    '<div class="ol1">\n'

            exam(sqall,listall)         

            if len(listall) != 0:
                all_list = show(listall)
                for i in range(int(all_list[1])):
                    html += '<li>' + all_list[0][i] + '</li>\n'
            
                #削除実行
                sql = 'delete from English_Words where number = ? and word = ? and japanese = ?' ,(v1,v2,v3, )
                cur.execute(*sql)
                con.commit()

                html +=  '</div>\n' \
                         'これらを削除しました。<br>\n'
            else:        
                html += '</div>\n' \
                        '該当するデータはありませんでした。<br>\n' \
            #削除ここまで    


        #間違えた問題、未回答問題表示
        elif wordall != "0":
            num = len(mistake)
            html += '間違えた問題<br>\n'
            for i in range(num):
                html += '<li>' + str(mistake[i][0]) + ' , ' + mistake[i][1] + ' , ' + mistake[i][2] + '</li>\n'
            html += '<br>未学習問題<br>\n'
            num = len(yet)
            for i in range(num):                        
                html += '<li>' + str(yet[i][0]) + ' , ' + yet[i][1] + ' , ' + yet[i][2] + '</li>\n'

        count[0] = 0

        html += '<a href="/">登録ページに戻る</a>\n' \
                '</body>\n'
        
        # カーソルと接続を閉じる
        cur.close()
        con.close()
    html += '</html>\n'
    html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]

# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python3 test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，http://localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる．
#  コマンドライン引数にポート番号を指定（python3 test_wsgi.py ポート番号）した場合は，
#  http://localhost:ポート番号 にアクセスする．
from wsgiref import simple_server
if __name__ == '__main__':
    port = 8080
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    server = simple_server.make_server('', port, application)
    server.serve_forever()
