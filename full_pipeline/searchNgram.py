'''
启发性搜索 N-Gram 词

functions: (List(List)) ---> List()
params:
    List(Jieba Lines)
return:
    List(N-Gram Word)
'''

from typing import List, Generator
from collections import defaultdict
import re


class HeuNgramSearch():
    def __init__(self,
                 splitGene, # type: Generator
                 N = 2, # type: int
                 threadOut = 0.5, # type: float
                 ):
        self.splitGene = splitGene
        self.N = N
        self.threadOut = threadOut
        self.ngramRes = defaultdict(int)
        self.compile = re.compile('([～？()…,\\./％„<>?;→°:÷″●≥—√\'\"‰{}〕Ⅱ≤|\\~`!@#$%^&\\[\\]*_\-\\+=、！，”。《》：＠；“‘『』】【～）・･＼\\└ω┘´（\\\\])')
        self.unionSentence = []

    # @staticmethod
    # def _create_split(splitRes):
    #     # None
    #     if not splitRes[0]:
    #         raise ValueError('no text data')
    #
    #     # 一维
    #     if isinstance(splitRes[0], list)


    def search(self):
        # count = 0
        for sentence in self.splitGene:
            sentence = re.sub('( )+', ' ', self.compile.sub('', ' '.join(sentence)).strip())
            # if count < 300:
            #     print(sentence)
            # count += 1
            self.unionSentence.append(sentence)

            ngram_list = self.ngrams(sentence = sentence, n = self.N)
            for val in ngram_list:
                self.ngramRes[''.join(val)] += 1

        self.ngramRes = dict(sorted(self.ngramRes.items(), key=lambda x: x[1], reverse=True))

        # --------------
        threadVal = self.quantile(self.ngramRes.values(), self.threadOut)

        self.ngramRes = self.arangeStruct(self.ngramRes, threadVal)

        # return self.resList[:int(len(self.resList) * self.threadOut)]



    @staticmethod
    def ngrams(sentence, n = 2):
        return list(zip(*[sentence.split()[i:] for i in range(n)]))


    @staticmethod
    def quantile(vals, # type: List
                 n, # type: int
                 ):
        length = len(set(vals))
        vals = sorted(vals, reverse = True)

        return vals[int(length * n)]

    @staticmethod
    def arangeStruct(res, thread):
        if isinstance(res, dict):
            return {k: v for k, v in res.items() if v >= thread}
        elif isinstance(res, list):
            return [x for x in res if x[1] >= thread]
        else:
            raise Exception('No support Struct temporarily')



# if __name__ == '__main__':
#     sample_text = ["是由古时期食肉类进化而来。在第三纪早期，古食肉类中的猫形类有数个分支：其中一支是古猎豹，贯穿各地质时期而进化为现今的猎豹；一支是犬齿高度特化的古剑齿虎类；一支是与古剑齿虎类相似的伪剑齿虎类；最后一支是古猫类。古剑齿虎类和伪剑齿虎类分别在第三纪早期和晚期灭绝，古猫类得以幸存。其中，类虎古猫就是现今的虎的祖先。后来，古猫类又分化为三支：真猫类、恐猫类和真剑齿虎类。其后二者均在第四纪冰河期灭绝，只有真猫类幸存下来，并分化成猫族和豹族两大类群而延续至21世纪，现今的虎，就是豹族成员之一。 [4]",
#                    "因此，要弄清楚虎的起源，就必须依靠颅骨化石，尤其是牙齿化石。邱占祥（1998年）认为，在中国已经发现的化石中，时代最早的虎化石可能是古中华虎（Panthera tigris palaeosinensis），这个种是1924年瑞典古生物学家Zdansky所建，标本是一个保存比较完好的属于同一个体的头骨、下牙床和一个寰椎（即第一颈椎），化石是当时在中国政府任矿业顾问的瑞典地质学家Anderson于1920年在河南渑池兰沟第三十八地点发现的，这个地点的确切地质年代尚不清楚。 [4]",
#                    "但是据有关专家推断，其时代至少在距现代200万年以上，这是因为，第一，含化石的岩性是红土，据Zdansky记述，和中国华北各地典型的含晚中新世三趾马动物群的红土很接近，而不像时代比较晚的第四纪的比较松散的黄色或绿色的砂岩或黄土，这表明它的时代可能介于上述两者之间；第二，在同一地点还发现过中华长鼻三趾马化石，这种化石主要发现于中国距今大约300万年至200万年的地层中，在极个别的情况下可能残存至距今100万年左右。关于这个种是否应该归入虎，科学界还有不同的看法。1967年德国科学家Hemmer著文详细讨论了这个种的性质。在很仔细地讨论了每一块骨头的形态特征并作了详细的测量和对比之后，得出的结论是，它的绝大部分特征都和虎更为接近，只是个体比虎小，而稍大于豹，因此应为虎的一个亚种（Panthera tigris palaeosinensis）。 [4]",
#                    "真正的虎的材料首次出现于陕西蓝田公王岭。化石发现得不多，只有一段上颌和一件不完整的下颌。这两件标本已经和虎很难区别了，在大小上比虎稍微大一点。公王岭地点的地质年代开始时认为可能只比周口店稍稍早一点，为中更新世初期，亦即距今大约60万年。从20世纪70年代开始，随着古地磁地层学的发展，人们逐渐认识到，公王岭含化石层位落在古地磁年表中松山反向期内的贾拉米洛正向事件之下，其地质年代大约应该是距今110万年左右。因此，可以说，至少距今100多万年前虎就和人类的祖先——蓝田人在一起生活。到中更新世时，也就是从距今60万年左右开始，虎的化石较多，至少在中国的东半部普遍可以发现。发现化石最多的，在华北是在著名的周口店北京人产地；而在华南则是在四川万县盐井沟裂隙堆积中，在盐井沟发现的虎化石，据统计至少有46个个体。 [4]",
#                    "关于虎的历史起源，比较公认的观点是：200万年前虎起源于东亚（即现今华南虎的分布区），然后沿着两个主要方向扩散，即虎沿西北方向的森林和河流系统进入亚洲西南部；沿南和西南方向进入东南亚及印度次大陆，一部分最终进入印度尼西亚群岛，在向亚洲其它地域扩散和辐射适应的过程中，虎演化为9个亚种，即华南虎、西伯利亚虎、孟加拉虎、印支虎、马来虎、苏门答腊虎、巴厘虎、爪哇虎和里海虎。由此可见，虎曾经广泛分布在西起土耳其，东至中国和俄罗斯海岸，北起西伯利亚，南至印度尼西亚群岛的辽阔土地上。至20世纪中叶，里海虎、爪哇虎、巴厘虎已经灭绝。中国曾经分布有华南虎、东北虎（西伯利亚虎）、孟加拉虎、印支虎（东南亚虎）、里海虎（新疆虎）（已灭绝）等5个亚种。由于生活地区的不同，以及个体大小、体毛的长短厚薄、毛色的深浅浓淡、条纹的多寡疏密、尾巴的粗细等形态上的一些差异。 [5]",
#                    "现代虎的祖先是一种叫做“中国古猫”的小型食肉类，大约是在距今300万年的更新世以后在地球上出现的，与人类的出现时间较为接近，而且可能曾与人类的祖先——蓝田人一起生活过。由于气候的变迁促进了动物群的演变、分化和迁移，虎便从发源地向亚洲西部、南部等各地逐渐扩散，向西发展的一支经蒙古、新疆和中亚直抵伊朗北部和高加索南部，但没能过阿拉伯沙漠进入非洲，也没能越过高加索山脉进入欧洲；向南发展的一支又分为两个分支，一个分支进入朝鲜半岛，受阻于朝鲜海峡，未能踏上日本列岛；另一个分支通过华北、华中和华南，进入中南半岛。到这里后，又分成两股，一股向西通过缅甸、孟加拉国，直抵印度半岛南端，另一股继续向南，沿马来西亚半岛南下，渡过狭长的马六甲海峡，登上印度尼西亚的苏门答腊、爪哇和巴厘等岛屿。",
#                    "虎的体态雄伟，毛色绮丽，头圆，吻宽，眼大，嘴边长着白色间有黑色的硬须，长达15厘米左右。颈部粗而短，几乎与肩部同宽，肩部、胸部、腹部和臀部均较窄，呈侧扁状，四肢强健，犬齿和爪极为锋利，嘴上长有长而硬的虎须，全身底色橙黄，腹面及四肢内侧为白色，背面有双行的黑色纵纹，尾上约有10个黑环，眼上方有一个白色区，故有“吊睛白额虎”之称，前额的黑纹颇似汉字中的“王”字，更显得异常威武，因此被誉为“山中之王”或“兽中之王”。 [5]",
#                    "虎强壮高大，毛色从北而南呈黄色到红色渐变，有深色条纹。不同于狮子吻长所以脸廓狭长的特点，老虎吻部较短，显得头大而圆。"]
#
#     import jieba
#
#     def splitgene(text):
#         for x in text:
#             yield jieba.lcut(x)
#
#
#     splitGene = splitgene(sample_text)
#
#
#     a = HeuNgramSearch(splitGene=splitGene)
#     a.search()
#     print(a.ngramRes)

