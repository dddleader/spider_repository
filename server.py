import sanic
import os, time, csv
import json as ger_json
from sanic.response import json
from sanic.response import file as res_file
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False 

app = sanic.Sanic("mySanic")

app.static("/static","./static")

# 上传影评数据文件接口
@app.route("/v1/movie/crawled/upload", methods=['GET', 'POST'])
async def upload(request):
    if request.method == 'POST':
        allow_type = ['.json']
        file = request.files.get('file')
        type = os.path.splitext(file.name)
        if len(type) == 1 or type[1] not in allow_type:
            return json({"code": 0, "msg": "file's format is error!"})
        path = "./upload"
        now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
        file_name = now_time + '_' + type[0] + ".json"
        with open(path + '/' + file_name, "wb") as f:
            f.write(file.body)
        f.close()
        convert_movie(path + '/' + file_name)
        return json({"code": 1, "msg": "upload successfully!", "data": None})
    elif request.method == 'GET':
        return await res_file('./static/upload.html', headers={'Content-Type': 'text/html; charset=utf-8'})

# 同步函数，提取并存储电影信息
def convert_movie(file_name):
    with open(file_name, "r", encoding = 'UTF-8') as file:
        body = ger_json.load(file)
        file.close()
    keys = []
    for key in body[0][0].keys():
        if not type(body[0][0][key]) == type({}) and not type(body[0][0][key]) == type([]):
            keys.append(key.strip())
    now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    csv_name = now_time + "_movie.csv"
    with open('./csv/' + csv_name, "w+", newline='', encoding='UTF-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        for item in body[0]:
            writer.writerow(item)
        file.close()
    return json({"code": 1, "msg": "convert successfully!", "data": None})

# 查询文件
@app.route("/v1/movie/csv", methods=['GET'])
async def get_files(request):
    filename = request.args.get('filename')
    file_info_list = []
    if not filename == None and os.path.isfile('./csv/'+filename):
        file_info_list = [{'filename':filename, 'filesize':os.path.getsize('./csv/'+filename)}]
    else:
        for root, dirs, files in os.walk('./csv/'):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)
                file_info = {
                    'file_name': file_name,
                    'file_size': file_size
                }
                file_info_list.append(file_info)

    return json({"code": 1, "msg": "query successfully!", "data": file_info_list})

# 获取电影信息
@app.route("/v1/movie/info", methods=['GET'])
async def get_movies_info(request):
    if request.args.get('filename') == None:
        return json({"code": 0, "msg": "missing filename!", "data": None})
    path = './csv'
    filename = path + '/' + request.args.get('filename')
    #movie_id = request.args.get('movie_id')
    if filename != None and not os.path.exists(filename):
        return json({"code": -1, "message": "the filename is none or the file is not exist"})
    if not filename.endswith("movie.csv"):
        return json({"code": 0, "message": "the file is not about movie!"})
		
    movies = []
    with open(filename, 'r', encoding='UTF-8') as file:
        n_csv = list(csv.reader(file))
        header = n_csv[0]
        for i in range(1, len(n_csv)):
            n_row = n_csv[i]
            movie = {}
            for j in range(0, len(header)):
                movie[header[j]] = n_row[j]
            movies.append(movie)
            #if movie_id != None and movie_id == movie["movie_id"]:
            #    movies = [movie]
            #    break
        file.close()
    return json({"code": 1, "msg": "query successfully!", "data": movies})

#
@app.route("v1/movie/country_analysis", methods=['GET'])
async def get_country_analysis(request):
    filename = request.args.get('filename')
    if filename == None:
        return json({"code": 0, "msg": "missing filename!", "data": None})
    if request.args.get('number') != None:
        number = int(request.args.get('number'))
    else:
        number = 0
    return await res_file( pie_chart("制片国家/地区", filename, number, "country_pie_chart"), headers={'Content-Disposition': 'attachment'} )

@app.route("v1/movie/language_analysis", methods=['GET'])
async def get_language_analysis(request):
    filename = request.args.get('filename')
    if filename == None:
        return json({"code": 0, "msg": "missing filename!", "data": None})
    if request.args.get('number') != None:
        number = int(request.args.get('number'))
    else:
        number = 0
    return await res_file( pie_chart("语言", filename, number, "language_pie_chart"), headers={'Content-Disposition': 'attachment'} )

@app.route("v1/movie/type_analysis", methods=['GET'])
async def get_type_analysis(request):
    filename = request.args.get('filename')
    if filename == None:
        return json({"code": 0, "msg": "missing filename!", "data": None})
    if request.args.get('number') != None:
        number = int(request.args.get('number'))
    else:
        number = 0
    return await res_file( pie_chart("类型", filename, number, "type_pie_chart"), headers={'Content-Disposition': 'attachment'} )

def pie_chart(keyname, filename, number, output_filename):
    count = 0
    with open('./csv/'+filename, 'r', encoding='UTF-8') as file:
        n_csv = list(csv.reader(file))
        header = n_csv[0]
        index = header.index(keyname)
        data = {}
        total = 0
        for i in range(1, len(n_csv)):
            n_row = n_csv[i]
            items = n_row[index].split('/')
            for item in items:
                if item not in data:
                    data[item] = 1
                else:
                    data[item] +=1
                total += 1
            count += 1
            if count == number and number > 0:
                break

        data_edit = {'其他':0}
        for i in data:
            if data[i]/total > 0.01:
                data_edit[i] = data[i]
            else:
                data_edit['其他'] += 1
        del data
        if data_edit['其他'] == 0:
            data_edit.pop('其他')
    
    labels = list(data_edit.keys())
    sizes = list(data_edit.values())
    
    plt.figure()
    
    # 设置饼状图的颜色
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    
    # 创建饼状图
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    
    # 添加标题
    plt.title(keyname+'饼状图')
    
    # 显示图形
    plt.axis('equal')
    filepath = './pie_chart/'+filename[:-4]+'_'+str(number)+'_'+output_filename+'.png'
    plt.savefig(filepath)
    return filepath


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

	
