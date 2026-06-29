# 序列分类学分析报告

## 目录

- [1. 方法](#1-方法)
  - [1.1 分析流程](#11-分析流程)
  - [1.2 主要软件工具](#12-主要软件工具)
- [2. 结果](#2-结果)
  - [2.1 总体情况](#21-总体情况)
  - [2.2 界（Kingdom）水平](#22-界kingdom水平)
  - [2.3 门（Phylum）水平](#23-门phylum水平)
  - [2.4 纲（Class）水平](#24-纲class水平)
  - [2.5 目（Order）水平](#25-目order水平)
  - [2.6 科（Family）水平](#26-科family水平)
  - [2.7 属（Genus）水平](#27-属genus水平)
  - [2.8 种（Species）水平](#28-种species水平)
- [3. 结论](#3-结论)

## 1. 方法

### 1.1 分析流程

本分析流程包括四个主要步骤：

**1. 序列采样**

从原始FASTQ文件中随机抽取1000条序列，转换为FASTA格式，用于后续的BLAST比对分析。采样采用流式处理方式，通过管道直接完成格式转换和随机采样，大幅提升处理效率。

**2. BLAST序列比对**

使用BLASTN工具将采样序列与NCBI核酸数据库（core_nt）进行同源性比对。每个查询序列最多保留10个最佳匹配结果，设置E值阈值为1e-5，序列相似性阈值为95%，查询覆盖率阈值为85%。比对采用48线程并行计算以提高速度。

```pseudocode
INPUT: query.fa, database, output.tsv, max_target_seqs, num_threads
BEGIN
    blastn(
        -query query.fa
        -db database
        -task blastn
        -word_size 11
        -evalue 1e-5
        -perc_identity 95
        -qcov_hsp_perc 85
        -max_target_seqs max_target_seqs
        -max_hsps 1
        -dust no
        -soft_masking false
        -num_threads num_threads
        -outfmt "6 qseqid sseqid sscinames pident length
                 mismatch gapopen qstart qend sstart send
                 qcovs evalue bitscore stitle"
        -out output.tsv
    )
END
```

**3. 物种注释信息添加**

利用TaxonKit工具将BLAST结果中的物种名称转换为NCBI分类学ID（TaxID），并获取从界到种的完整分类学信息，包括界（Kingdom）、门（Phylum）、纲（Class）、目（Order）、科（Family）、属（Genus）、种（Species）七个分类层级。

对于每条比对成功的序列，BLAST可能返回多个匹配结果（本分析设置为最多10个）。在添加物种注释信息时，我们选取每条序列的最佳匹配结果（即第一个比对结果）进行注释，以确保分类学信息的准确性和一致性。最佳匹配结果通常具有最高的序列相似性和比对得分。

**4. 分类学统计与可视化**

对每个分类水平的序列丰度进行统计分析，提取Top 5丰度的分类单元，并生成风玫瑰图（极坐标条形图）进行可视化展示。

### 1.2 主要软件工具

| 软件工具 | 版本 | 用途 |
|---|---|---|
| SeqKit | 2.9.0 | 序列格式转换与随机采样 |
| BLAST+ | 2.17.0+ | 序列同源性比对 |
| TaxonKit | 0.20.0 | 分类学信息查询与转换 |
| Python | 3.12.2 | 数据统计与可视化 |

## 2. 结果

### 2.1 总体情况

本次分析从原始FASTQ文件中随机抽取了**1000**条序列进行BLAST比对分析。其中，**374**条序列能够与NCBI核酸数据库中的序列产生有效比对结果，比对成功率为**37.4%**。对这374条比对成功的序列均进行了分类学注释。

### 2.2 界（Kingdom）水平

| 界 | 序列数 | 百分比 |
|---|---:|---:|
| Metazoa（后生动物） | 366 | 97.86% |
| Pseudomonadati | 4 | 1.07% |
| Fungi（真菌） | 2 | 0.53% |
| unknown | 1 | 0.27% |
| Bacillati | 1 | 0.27% |

结果显示，在374条比对成功的序列中，有366条序列被鉴定为后生动物（Metazoa），占所有比对成功序列的97.86%，表明后生动物在样本中占绝对优势。

![Kingdom分布](taxon_info_Kingdom_top5_pie.png)

### 2.3 门（Phylum）水平

| 门 | 序列数 | 百分比 |
|---|---:|---:|
| Chordata（脊索动物） | 365 | 97.59% |
| Pseudomonadota | 2 | 0.53% |
| Campylobacterota | 1 | 0.27% |
| unknown | 1 | 0.27% |
| Actinomycetota | 1 | 0.27% |
| Others | 4 | 1.07% |

在374条比对成功的序列中，有365条序列被鉴定为脊索动物门（Chordata），占所有比对成功序列的97.59%，显示脊索动物门在样本中占据主导地位。

![Phylum分布](taxon_info_Phylum_top5_pie.png)

### 2.4 纲（Class）水平

| 纲 | 序列数 | 百分比 |
|---|---:|---:|
| Mammalia（哺乳纲） | 356 | 95.19% |
| Actinopteri（辐鳍鱼纲） | 4 | 1.07% |
| Aves（鸟纲） | 2 | 0.53% |
| Lepidosauria | 1 | 0.27% |
| Amphibia（两栖纲） | 1 | 0.27% |
| Others | 10 | 2.67% |

在374条比对成功的序列中，有356条序列被鉴定为哺乳纲（Mammalia），占所有比对成功序列的95.19%，显示哺乳纲是样本中最主要的类群。

![Class分布](taxon_info_Class_top5_pie.png)

### 2.5 目（Order）水平

| 目 | 序列数 | 百分比 |
|---|---:|---:|
| Artiodactyla（偶蹄目） | 245 | 65.51% |
| Primates（灵长目） | 102 | 27.27% |
| Carnivora（食肉目） | 5 | 1.34% |
| Passeriformes（雀形目） | 2 | 0.53% |
| unknown | 2 | 0.53% |
| Others | 18 | 4.81% |

在374条比对成功的序列中，偶蹄目（Artiodactyla）和灵长目（Primates）是两个主要类群。其中，245条序列被鉴定为偶蹄目，占所有比对成功序列的65.51%；102条序列被鉴定为灵长目，占27.27%。

![Order分布](taxon_info_Order_top5_pie.png)

### 2.6 科（Family）水平

| 科 | 序列数 | 百分比 |
|---|---:|---:|
| Suidae（猪科） | 242 | 64.71% |
| Cercopithecidae（猴科） | 69 | 18.45% |
| Hominidae（人科） | 32 | 8.56% |
| Phocidae（海豹科） | 3 | 0.80% |
| Equidae（马科） | 1 | 0.27% |
| Others | 27 | 7.22% |

在374条比对成功的序列中，猪科（Suidae）、猴科（Cercopithecidae）和人科（Hominidae）是三个主要科。其中，242条序列被鉴定为猪科，占所有比对成功序列的64.71%；69条序列被鉴定为猴科，占18.45%；32条序列被鉴定为人科，占8.56%。

![Family分布](taxon_info_Family_top5_pie.png)

### 2.7 属（Genus）水平

| 属 | 序列数 | 百分比 |
|---|---:|---:|
| Sus（猪属） | 215 | 57.49% |
| Macaca（猕猴属） | 52 | 13.90% |
| Phacochoerus（疣猪属） | 27 | 7.22% |
| Homo（人属） | 26 | 6.95% |
| Papio（狒狒属） | 5 | 1.34% |
| Others | 49 | 13.10% |

在374条比对成功的序列中，猪属（Sus）和猕猴属（Macaca）是两个主要属。其中，215条序列被鉴定为猪属，占所有比对成功序列的57.49%；52条序列被鉴定为猕猴属，占13.90%。

![Genus分布](taxon_info_Genus_top5_pie.png)

### 2.8 种（Species）水平

| 种 | 序列数 | 百分比 |
|---|---:|---:|
| Sus scrofa（野猪/家猪） | 214 | 57.22% |
| Phacochoerus africanus（普通疣猪） | 27 | 7.22% |
| Homo sapiens（智人） | 26 | 6.95% |
| Macaca mulatta（恒河猴） | 20 | 5.35% |
| Macaca fascicularis（食蟹猴） | 17 | 4.55% |
| Others | 70 | 18.72% |

在374条比对成功的序列中，野猪/家猪（Sus scrofa）是最主要的物种。其中，214条序列被鉴定为野猪/家猪，占所有比对成功序列的57.22%；27条序列被鉴定为普通疣猪（Phacochoerus africanus），占7.22%；26条序列被鉴定为智人（Homo sapiens），占6.95%。

![Species分布](taxon_info_Species_top5_pie.png)

## 3. 结论

1. **物种组成高度集中**：在比对成功的374条序列中，绝大多数（97.86%）属于后生动物界，其中哺乳纲占95.19%，显示样本以哺乳动物为主。

2. **主要物种明确**：在比对成功的序列中，偶蹄目猪科猪属的野猪/家猪（Sus scrofa）是最主要的物种，占所有比对成功序列的57.22%，表明样本可能来源于猪相关的研究或环境。

3. **灵长类占比较高**：在比对成功的序列中，灵长目序列占27.27%，包括恒河猴（Macaca mulatta, 5.35%）、食蟹猴（Macaca fascicularis, 4.55%）和智人（Homo sapiens, 6.95%），可能存在一定程度的人源污染或样本中包含灵长类动物成分。

4. **物种多样性**：除了主要物种外，还有约18.72%的比对成功序列分布在其他物种中，显示样本具有一定的物种多样性。

5. **分类学注释完整性**：仅有少量比对成功的序列（0.27%）无法确定分类学信息，整体注释效果良好。
