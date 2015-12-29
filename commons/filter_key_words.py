# coding:utf-8
# !/usr/bin/env python
from decorated.base.dict import DefaultDict

from commons import stringutil

__author__ = 'wanglei'

key_words_list = [u'SB', u'草你妈', u'fuck you', u'法轮大法', u'草你大爷', u'FUCK']


class FilterKeyWords(object):
    """ 过滤敏感词类

    """

    traditional_chinese = u"皚藹礙愛翺襖奧壩罷擺敗頒辦絆幫綁鎊謗剝飽寶報鮑輩貝鋇狽備憊繃筆畢斃閉邊編貶變辯辮鼈癟瀕濱賓擯餅撥缽鉑駁蔔補參蠶殘慚慘燦蒼艙倉滄廁側冊測層詫攙摻蟬饞讒纏鏟産闡顫場嘗長償腸廠暢鈔車徹塵陳襯撐稱懲誠騁癡遲馳恥齒熾沖蟲寵疇躊籌綢醜櫥廚鋤" \
                          u"雛礎儲觸處傳瘡闖創錘純綽辭詞賜聰蔥囪從叢湊竄錯達帶貸擔單鄲撣膽憚誕彈當擋黨蕩檔搗島禱導盜燈鄧敵滌遞締點墊電澱釣調叠諜疊釘頂錠訂東動棟凍鬥犢獨讀賭鍍鍛斷緞兌隊對噸頓鈍奪鵝額訛惡餓兒爾餌貳發罰閥琺礬釩煩範販飯訪紡飛廢費紛墳奮憤糞豐楓鋒" \
                          u"風瘋馮縫諷鳳膚輻撫輔賦複負訃婦縛該鈣蓋幹趕稈贛岡剛鋼綱崗臯鎬擱鴿閣鉻個給龔宮鞏貢鈎溝構購夠蠱顧剮關觀館慣貫廣規矽歸龜閨軌詭櫃貴劊輥滾鍋國過駭韓漢閡鶴賀橫轟鴻紅後壺護滬戶嘩華畫劃話懷壞歡環還緩換喚瘓煥渙黃謊揮輝毀賄穢會燴彙諱誨繪葷渾" \
                          u"夥獲貨禍擊機積饑譏雞績緝極輯級擠幾薊劑濟計記際繼紀夾莢頰賈鉀價駕殲監堅箋間艱緘繭檢堿鹼揀撿簡儉減薦檻鑒踐賤見鍵艦劍餞漸濺澗漿蔣槳獎講醬膠澆驕嬌攪鉸矯僥腳餃繳絞轎較稭階節莖驚經頸靜鏡徑痙競淨糾廄舊駒舉據鋸懼劇鵑絹傑潔結誡屆緊錦僅謹進" \
                          u"晉燼盡勁荊覺決訣絕鈞軍駿開凱顆殼課墾懇摳庫褲誇塊儈寬礦曠況虧巋窺饋潰擴闊蠟臘萊來賴藍欄攔籃闌蘭瀾讕攬覽懶纜爛濫撈勞澇樂鐳壘類淚籬離裏鯉禮麗厲勵礫曆瀝隸倆聯蓮連鐮憐漣簾斂臉鏈戀煉練糧涼兩輛諒療遼鐐獵臨鄰鱗凜賃齡鈴淩靈嶺領餾劉龍聾嚨籠" \
                          u"壟攏隴樓婁摟簍蘆盧顱廬爐擄鹵虜魯賂祿錄陸驢呂鋁侶屢縷慮濾綠巒攣孿灤亂掄輪倫侖淪綸論蘿羅邏鑼籮騾駱絡媽瑪碼螞馬罵嗎買麥賣邁脈瞞饅蠻滿謾貓錨鉚貿麽黴沒鎂門悶們錳夢謎彌覓綿緬廟滅憫閩鳴銘謬謀畝鈉納難撓腦惱鬧餒膩攆撚釀鳥聶齧鑷鎳檸獰甯擰濘" \
                          u"鈕紐膿濃農瘧諾歐鷗毆嘔漚盤龐賠噴鵬騙飄頻貧蘋憑評潑頗撲鋪樸譜臍齊騎豈啓氣棄訖牽扡釺鉛遷簽謙錢鉗潛淺譴塹槍嗆牆薔強搶鍬橋喬僑翹竅竊欽親輕氫傾頃請慶瓊窮趨區軀驅齲顴權勸卻鵲讓饒擾繞熱韌認紉榮絨軟銳閏潤灑薩鰓賽傘喪騷掃澀殺紗篩曬閃陝贍繕" \
                          u"傷賞燒紹賒攝懾設紳審嬸腎滲聲繩勝聖師獅濕詩屍時蝕實識駛勢釋飾視試壽獸樞輸書贖屬術樹豎數帥雙誰稅順說碩爍絲飼聳慫頌訟誦擻蘇訴肅雖綏歲孫損筍縮瑣鎖獺撻擡攤貪癱灘壇譚談歎湯燙濤縧騰謄銻題體屜條貼鐵廳聽烴銅統頭圖塗團頹蛻脫鴕馱駝橢窪襪彎灣" \
                          u"頑萬網韋違圍爲濰維葦偉僞緯謂衛溫聞紋穩問甕撾蝸渦窩嗚鎢烏誣無蕪吳塢霧務誤錫犧襲習銑戲細蝦轄峽俠狹廈鍁鮮纖鹹賢銜閑顯險現獻縣餡羨憲線廂鑲鄉詳響項蕭銷曉嘯蠍協挾攜脅諧寫瀉謝鋅釁興洶鏽繡虛噓須許緒續軒懸選癬絢學勳詢尋馴訓訊遜壓鴉鴨啞亞訝" \
                          u"閹煙鹽嚴顔閻豔厭硯彥諺驗鴦楊揚瘍陽癢養樣瑤搖堯遙窯謠藥爺頁業葉醫銥頤遺儀彜蟻藝億憶義詣議誼譯異繹蔭陰銀飲櫻嬰鷹應纓瑩螢營熒蠅穎喲擁傭癰踴詠湧優憂郵鈾猶遊誘輿魚漁娛與嶼語籲禦獄譽預馭鴛淵轅園員圓緣遠願約躍鑰嶽粵悅閱雲鄖勻隕運蘊醞暈韻" \
                          u"雜災載攢暫贊贓髒鑿棗竈責擇則澤賊贈紮劄軋鍘閘詐齋債氈盞斬輾嶄棧戰綻張漲帳賬脹趙蟄轍鍺這貞針偵診鎮陣掙睜猙幀鄭證織職執紙摯擲幟質鍾終種腫衆謅軸皺晝驟豬諸誅燭矚囑貯鑄築駐專磚轉賺樁莊裝妝壯狀錐贅墜綴諄濁茲資漬蹤綜總縱鄒詛組鑽緻鐘麼為隻" \
                          u"兇準啟闆裡靂餘鍊洩"
    simplified_chinese = u"皑蔼碍爱翱袄奥坝罢摆败颁办绊帮绑镑谤剥饱宝报鲍辈贝钡狈备惫绷笔毕毙闭边编贬变辩辫鳖瘪濒滨宾摈饼拨钵铂驳卜补参蚕残惭惨灿苍舱仓沧厕侧册测层诧搀掺蝉馋谗缠铲产阐颤场尝长偿肠厂畅钞车彻尘陈衬撑称惩诚骋痴迟驰耻齿炽冲虫宠畴踌筹绸丑橱厨锄雏" \
                         u"础储触处传疮闯创锤纯绰辞词赐聪葱囱从丛凑窜错达带贷担单郸掸胆惮诞弹当挡党荡档捣岛祷导盗灯邓敌涤递缔点垫电淀钓调迭谍叠钉顶锭订东动栋冻斗犊独读赌镀锻断缎兑队对吨顿钝夺鹅额讹恶饿儿尔饵贰发罚阀珐矾钒烦范贩饭访纺飞废费纷坟奋愤粪丰枫锋风" \
                         u"疯冯缝讽凤肤辐抚辅赋复负讣妇缚该钙盖干赶秆赣冈刚钢纲岗皋镐搁鸽阁铬个给龚宫巩贡钩沟构购够蛊顾剐关观馆惯贯广规硅归龟闺轨诡柜贵刽辊滚锅国过骇韩汉阂鹤贺横轰鸿红后壶护沪户哗华画划话怀坏欢环还缓换唤痪焕涣黄谎挥辉毁贿秽会烩汇讳诲绘荤浑伙" \
                         u"获货祸击机积饥讥鸡绩缉极辑级挤几蓟剂济计记际继纪夹荚颊贾钾价驾歼监坚笺间艰缄茧检碱硷拣捡简俭减荐槛鉴践贱见键舰剑饯渐溅涧浆蒋桨奖讲酱胶浇骄娇搅铰矫侥脚饺缴绞轿较秸阶节茎惊经颈静镜径痉竞净纠厩旧驹举据锯惧剧鹃绢杰洁结诫届紧锦仅谨进晋" \
                         u"烬尽劲荆觉决诀绝钧军骏开凯颗壳课垦恳抠库裤夸块侩宽矿旷况亏岿窥馈溃扩阔蜡腊莱来赖蓝栏拦篮阑兰澜谰揽览懒缆烂滥捞劳涝乐镭垒类泪篱离里鲤礼丽厉励砾历沥隶俩联莲连镰怜涟帘敛脸链恋炼练粮凉两辆谅疗辽镣猎临邻鳞凛赁龄铃凌灵岭领馏刘龙聋咙笼垄" \
                         u"拢陇楼娄搂篓芦卢颅庐炉掳卤虏鲁赂禄录陆驴吕铝侣屡缕虑滤绿峦挛孪滦乱抡轮伦仑沦纶论萝罗逻锣箩骡骆络妈玛码蚂马骂吗买麦卖迈脉瞒馒蛮满谩猫锚铆贸么霉没镁门闷们锰梦谜弥觅绵缅庙灭悯闽鸣铭谬谋亩钠纳难挠脑恼闹馁腻撵捻酿鸟聂啮镊镍柠狞宁拧泞钮" \
                         u"纽脓浓农疟诺欧鸥殴呕沤盘庞赔喷鹏骗飘频贫苹凭评泼颇扑铺朴谱脐齐骑岂启气弃讫牵扦钎铅迁签谦钱钳潜浅谴堑枪呛墙蔷强抢锹桥乔侨翘窍窃钦亲轻氢倾顷请庆琼穷趋区躯驱龋颧权劝却鹊让饶扰绕热韧认纫荣绒软锐闰润洒萨鳃赛伞丧骚扫涩杀纱筛晒闪陕赡缮伤" \
                         u"赏烧绍赊摄慑设绅审婶肾渗声绳胜圣师狮湿诗尸时蚀实识驶势释饰视试寿兽枢输书赎属术树竖数帅双谁税顺说硕烁丝饲耸怂颂讼诵擞苏诉肃虽绥岁孙损笋缩琐锁獭挞抬摊贪瘫滩坛谭谈叹汤烫涛绦腾誊锑题体屉条贴铁厅听烃铜统头图涂团颓蜕脱鸵驮驼椭洼袜弯湾顽" \
                         u"万网韦违围为潍维苇伟伪纬谓卫温闻纹稳问瓮挝蜗涡窝呜钨乌诬无芜吴坞雾务误锡牺袭习铣戏细虾辖峡侠狭厦锨鲜纤咸贤衔闲显险现献县馅羡宪线厢镶乡详响项萧销晓啸蝎协挟携胁谐写泻谢锌衅兴汹锈绣虚嘘须许绪续轩悬选癣绚学勋询寻驯训讯逊压鸦鸭哑亚讶阉" \
                         u"烟盐严颜阎艳厌砚彦谚验鸯杨扬疡阳痒养样瑶摇尧遥窑谣药爷页业叶医铱颐遗仪彝蚁艺亿忆义诣议谊译异绎荫阴银饮樱婴鹰应缨莹萤营荧蝇颖哟拥佣痈踊咏涌优忧邮铀犹游诱舆鱼渔娱与屿语吁御狱誉预驭鸳渊辕园员圆缘远愿约跃钥岳粤悦阅云郧匀陨运蕴酝晕韵杂" \
                         u"灾载攒暂赞赃脏凿枣灶责择则泽贼赠扎札轧铡闸诈斋债毡盏斩辗崭栈战绽张涨帐账胀赵蛰辙锗这贞针侦诊镇阵挣睁狰帧郑证织职执纸挚掷帜质钟终种肿众诌轴皱昼骤猪诸诛烛瞩嘱贮铸筑驻专砖转赚桩庄装妆壮状锥赘坠缀谆浊兹资渍踪综总纵邹诅组钻致钟么为只凶" \
                         u"准启板里雳余链泄"

    def __init__(self, *key_words):
        """ 初期话类对象属性

        :return:
        :rtype:
        """
        self.traditional_chinese = list(self.traditional_chinese)

        self.simplified_chinese = list(self.simplified_chinese)

        self.simplified_chinese_dict = dict(zip(self.traditional_chinese, self.simplified_chinese))
        # 创建一个跟节点
        self._root = FilterKeyWordsNode()
        # 关键词去重
        key_words = list(set(key_words))
        # 按照长度有短到高排序
        key_words.sort(key=lambda x: len(x))
        # 转换数组里的数据
        tran_key_words = []
        for key_word in key_words:
            key_word = self.translation(key_word)
            tran_key_words.append(key_word)
        # 循环时所需要的索引
        start_index = len(tran_key_words[0])
        end_index = len(tran_key_words[-1])
        # 构造树形节点
        for i in range(start_index, end_index+1):
            start_word_list = [key_word[0:i] for key_word in tran_key_words if len(key_word) >= i]
            for start_word in start_word_list:
                temp_node = self._root

                for j in range(len(start_word)):
                    key = start_word[j]
                    if temp_node.child is None:
                        temp_node.child = DefaultDict()
                    if temp_node.child[key] is None:
                        temp_node.child[key] = FilterKeyWordsNode()
                        word = start_word[0:j+1]
                        try:
                            tran_key_words.index(word)
                            temp_node.child[key].is_end = True
                        except Exception:
                            temp_node.child[key].is_end = False
                    temp_node = temp_node.child[key]

    def find(self, text):
        """ 查询需要过滤的词的位置

        :param text:
        :type text:
        :return: 返回在文本中的开始和结束的位置
        :rtype: dict
        """

        find_result = dict()

        if self._root is None:
            return find_result

        if stringutil.is_blank(text):
            return find_result

        start = 0

        while start < len(text):
            length = 0
            first_char = text[start + length]
            node = self._root

            while node.child.get(first_char, None) is None and start < len(text) - 1:
                start += 1
                first_char = text[start + length]

            while node.child is not None and node.child.get(first_char, None) is not None:
                node = node.child[first_char]
                length += 1

                if start + length == len(text):
                    break
                first_char = text[start + length]

            if node.is_end:
                find_result[start] = start + length
                start = start + length - 1
            start += 1
        return find_result

    def simple_replace(self, text, replace_dict=None):
        """ 简单替换为 *

        :param text:
        :type text:
        :param replace_dict:
        :type replace_dict:
        :return:
        :rtype:
        """

        if replace_dict is None:
            find_result = self.find(text)
        else:
            find_result = replace_dict

        for start_index, end_index in find_result.items():

            count = end_index - start_index
            text = text.replace(text[start_index:end_index], '*'*count)

        return text

    def get_key_words(self, text):
        """ 获取关键次的索引

        :param text:
        :type text:
        :return:
        :rtype: dict
        """

        find_result = self.find(text)

        return find_result if len(find_result) > 0 else None

    def translation(self, text):
        """ 将文转换成统一的格式

        :param text:
        :type text:
        :return:
        :rtype:
        """

        text_temp = text
        if isinstance(text, basestring):
            text_temp = list(text)

        for i in range(len(text_temp)):

            # 获取union_code的十进制数值
            inside_code = ord(text_temp[i])
            # 全角文字转换成半角
            if 65375 > inside_code > 65280:
                text_temp[i:i+1] = self.str_q2b(text_temp[i]).decode('cp936')
            # 大写转换成小写
            if 91 > inside_code > 64:
                text_temp[i:i+1] = text_temp[i].lower()
            # 繁体字转换简体
            if 40959 > inside_code > 19968:
                new_string = self.simplified_chinese_dict.get(text_temp[i], '')
                if new_string:
                    text_temp[i:i+1] = new_string

        return ''.join(text_temp) if isinstance(text, basestring) else text_temp


    @staticmethod
    def str_q2b(ustring):
        """全角转半角"""
        r_string = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif 65374 >= inside_code >= 65281:  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            r_string += unichr(inside_code)
        return r_string


class FilterKeyWordsNode(object):

    def __init__(self):

        self.child = DefaultDict()
        self.is_end = False

if __name__ == '__main__':
# #
    a = FilterKeyWords(*key_words_list)
#
    text_temp = u"你123d好发ABC否啊ａa风景皚藹FUCK"

    print a.translation(text_temp)

#     text_temp = list(text_temp)
#
#     print text_temp[0:1]
#
#     print text_temp
#
#     text_temp[0:1] = u"哈"
#
#     for b in text_temp:
#         print b
#     print a.simplified_chinese

    # print a.get_key_words(text_temp)
    #
    #
    #
    print a.simple_replace(a.translation(text_temp))
#     find_result = a.find(text_temp)
#     for start_index, end_index in find_result.items():
#         b = text_temp[start_index:end_index]
#         print b
#     print find_result
