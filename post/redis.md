![Redis](http://www.outman.com/wp-content/uploads/2012/03/redis-300dpi.png)


### 文章结构:

#### Redis是什么
#### 和其它NOSQL的比较
#### Redis的数据结构
#### 持久化策略
#### 常见问题和解决方法



##  Redis 是什么

* **Redis**是一个开源的使用ANSI C语言编写的基于内存的key/value存储系统，与memcache类似，但它支持的数据类型更为丰富，包括：字符串(string)、链表(list)、集合(set)、有序集合(sorted set)和hash table

* 性能极高 – Redis能支持超过 100K+ 每秒的读写频率。

* 原子 – Redis的所有操作都是原子性的，同时Redis还支持事务 (对几个操作全并后的原子性执行。)

* 目前的稳定版本是2.6.10，包括Github、Instagram 、Blizzard、 同内有新浪微博 ，ZAKER，多玩等都在产品中大量使用了Redis。

* redis自带了服务器和客户端，使用src/redis-server可以运行服务器，默认端口是6379，redis.conf有很多配置选项。
可以用src/redis-cli测试一下服务器是否正常，-h指定服务器ip。

* 其代码基于BSD协议开源，整个项目代码量只有2万多行（2.2版本），大家可以通过阅读代码在相对短的时间内学习到作者的设计理念和Redis的实现方式，做到知其然知其所以然。
(如果你读过其他项目的源码，再读Redis的源码，你就会知道Redis的实有多么的优雅)

* [try redis](http://try.redis.io/) 感受Redis 完成 hello world
<pre>
set key hello
append key " world!"
get key
</pre>



## Redis 与 Memcached
* 和Memcached不同，Redis并没有选择libevent。Libevent为了迎合通用性造成代码庞大(目前Redis代码还不到libevent的1/3)及牺牲了在特定平台的不少性能。Redis用libevent中两个文件修改实现了自己的epoll event loop。业界不少开发者也建议Redis使用另外一个libevent高性能替代libev，但是作者还是坚持Redis应该小巧并去依赖的思路。一个印象深刻的细节是编译Redis之前并不需要执行./configure。

* CAS问题。CAS是Memcached中比较方便的一种防止竞争修改资源的方法。CAS实现需要为每个cache key设置一个隐藏的cas token，cas相当value版本号，每次set会token需要递增，因此带来CPU和内存的双重开销，虽然这些开销很小，但是到单机10G+ cache以及QPS上万之后这些开销就会给双方相对带来一些细微性能差别。

* 这里可以引用作者的一段话来总结：

> 没有必要过多的关心性能，因为二者的性能都已经足够高了。由于Redis只使用单核，而Memcached可以使用多核，所以在比较上，平均每一个核上Redis在存储小数据时比Memcached性能更高。而在100k以上的数据中，Memcached性能要高于Redis，虽然Redis最近也在存储大数据的性能上进行优化，但是比起Memcached，还是稍有逊色。说了这么多，结论是，无论你使用哪一个，每秒处理请求的次数都不会成为瓶颈。（比如瓶颈可能会在网卡）
>
如果要说内存使用效率，使用简单的key-value存储的话，Memcached的内存利用率更高，而如果Redis采用hash结构来做key-value存储，由于其组合式的压缩，其内存利用率会高于Memcached。当然，这和你的应用场景和数据特性有关。
>
如果你对数据持久化和数据同步有所要求，那么推荐你选择Redis，因为这两个特性Memcached都不具备。即使你只是希望在升级或者重启系统后缓存数据不会丢失，选择Redis也是明智的。
>
Redis相比Memcached来说，拥有更多的数据结构和并支持更丰富的数据操作，通常在Memcached里，你需要将数据拿到客户端来进行类似的修改再set回去。这大大增加了网络IO的次数和数据体积。在Redis中，这些复杂的操作通常和一般的GET/SET一样高效。所以，如果你需要缓存能够支持更复杂的结构和操作，那么Redis会是不错的选择。
>
当然，最后还得说到你的具体应用需求。性能+适合应用才是正确的选择！

## MongoDB
![MongoDB](http://www.yankun.org/wp-content/uploads/2011/06/mongodb.png)

* 2010年风头最劲的NOSQL产品，很多公司开始尝鲜，我的前公司也是其中之一。

* MongoDB是一个介于关系数据库和非关系数据库之间的产品，是非关系数据库当中功能最丰富，最像关系数据库的。

* 基于文档模型，使用上非常灵活，但我觉得我也是它的很大的缺点。
* 文档模型是一种类似于json的文档格式，叫bson.

> mongoDB 的全局锁很变态，在版本2.2之前都是全局锁，即实例锁。
>
最新版， 2.2后的最细粒度是库级锁，应该没打算实现表锁和行锁。(这真是一个很大的坑爹，我在这吃了不少苦头了！！！)

<pre>
就是在同一个数据集里，每个文档的数据都不相同，Mongo是没有作限制的。
{'name':'Wasabi', 'age':30}
{'name':'joe', 'email':'test@aa.com'}
{'id':'AAA'}
</pre>
* 支持数组，索引，排序，范围查询，基本上Mysql 上有的功能，Mongo都有相应的支持。
* Mongo 的PHP客户端，是类型敏感的，这里已经给它坑过不少次了， 就是 10 和‘10’,它理解是不相同的。



## Redis 键
* Redis key值是二进制安全的，这意味着可以用任何二进制序列作为key值，从形如”foo”的简单字符串到一个JPEG文件的内容都可以。空字符串也是有效key值。

* 关于key的几条规则：
* 太长的键值不是个好主意，例如1024字节的键值就不是个好主意，不仅因为消耗内存，而且在数据中查找这类键值的计算成本很高。

* 太短的键值通常也不是好主意，如果你要用”u:1000:pwd”来代替”user:1000:password”，这没有什么问题，但后者更易阅读，并且由此增加的空间消耗相对于key object和value object本身来说很小。

* 最好坚持一种模式。例如：”object-type:id:field”就是个不错的注意，像这样”user:1000:password”。我喜欢对多单词的字段名中加上一个点，就像这样：”comment:1234:reply.to”。

##  Redis数据结构

### 字符串类型
* 这是最简单Redis类型。如果你只用这种类型，Redis就像一个可以持久化的memcached服务器（注：memcache的数据仅保存在内存中，服务器重启后，数据将丢失）。
<pre>
    $ redis-cli set mykey "my binary safe value"
    OK
    $ redis-cli get mykey
	my binary safe value
    
    // 自增类型
    redis 127.0.0.1:6379> incr bar
(integer) 1
redis 127.0.0.1:6379> incrby bar 2
(integer) 3
redis 127.0.0.1:6379> incrby bar 3
(integer) 6
</pre>

> 值可以是任何种类的字符串（包括二进制数据），例如你可以在一个键下保存一副jpeg图片。值的长度不能超过1GB。

### 列表类型
* 列表类型(list) 可以存储一个有序的字符串列表,常用的操作是向列表两端添加元素,或者获得列表的某一个片段.
* 使用双向链表实现的,所以向向列表两端添加元素的时间复杂度为O(1),获取越接近两端的元素速度就越快.
* LPUSH 向列表左边添加元素
* RPUSH 向列表右边添加元素
* LEN  返回元素个数,当键不存时会返回0

<pre>
// 向队尾添加三个元素,返加列表的元素个数
redis> RPUSH brands Apple Microsoft Google
(integer) 3

// 移除在队头的元素
redis> LPOP brands
"Apple"

redis> LLEN brands
(integer) 2

redis> LRANGE brands 0 -1
1) "Microsoft"
2) "Google"
</pre>

![双端链表](http://www.redisbook.com/en/latest/_images/graphviz-784672591f106642e353f784c9d64cec7a2adb26.svg)

* 其中， listNode 是双端链表的节点，
* prev 前驱节点 ,next 后继节点, 值value; 
> listNode 的 value 属性的类型是 void * ，说明这个双端链表对节点所保存的值的类型不做限制。
* 而 list 则是双端链表本身
* [参考资料](http://www.redisbook.com/en/latest/internal-datastruct/adlist.html)
<pre>
typedef struct list {

    // 表头指针
    listNode *head;

    // 表尾指针
    listNode *tail;

    // 节点数量
    unsigned long len;

    // 复制函数
    void *(*dup)(void *ptr);
    // 释放函数
    void (*free)(void *ptr);
    // 比对函数
    int (*match)(void *ptr, void *key);
} list;
</pre>

#### 检查是否有超出频率限制的实例
1. len得到列表的长度
2. 看长度是否已经超过最大限制
3. 如果未超过,加入一个元素
4. 如果超过限制,看是否在等待时间内,如果在,直接返回-1,如果不用等待,加入一个元素,修剪列表元素.
<pre>

    /**
     * 检查是否有超出频率限制
     * @param string $key_name
     * @param int $limit 最大数量
     * @param int $rate  频率,单位(秒)
     * @param int $life_time 生存时间,单位(秒)
     * @return number
     */
    function check_limit_rate($key_name, $limit = 10, $rate  = 60, $life_time=36000)
    {

        $redis = $this->redis;
        $now = time();
        $status = 1;
        
        $len = $redis->llen($key_name);

        if ($len ==0){
            $redis->expire($key_name, $life_time);
        }
        
        if ($len < $limit){
            $redis->lpush($key_name, $now);

            $status = $len+1;
        }
        else{
            $time = $redis->lindex($key_name, -1);    //返回列表key中，最后的元素
            
            
            if ($now - $time < $rate){
                // 频率超过了限制
                $status = -1;
            }
            else{
                
                $status = $limit;
                $redis->lpush($key_name, $now);
                $redis->ltrim($key_name, 0, $limit);
            }
        }
        return $status;
    }
</pre>

### 散列类型
* 散列类型适合存储对象：使用对象类别和ID构成键名，使用字段表示对象的属性，而字段值则存储属性值。例如要存储ID为2的汽车对象，可以分别使用名 color,name,price的3个字段来存储。这样做的目的比一用一个字符串来存储一个对象，粒度更小，修改起来会更灵活。
> 字段值只能是字符串，不支持其他数据类型，也就是说不能嵌套。
>
一个散列类型键可以包含最多2^32 - 1个字段。

<pre>
> HSET car price 500
(integer) 1
> HSET car name BMW
(integer) 1
> HGET car name
"BMW"
> HGETALL car
1) "price"
2) "500"
3) "name"
4) "BMW"
</pre>

### 集合类型
![set](http://www.redisbook.com/en/latest/_images/graphviz-2f54a5b62b3507f0e6d579358e426c78b0dfbd5c.svg)

* Redis集合是未排序的集合，其元素是二进制安全的字符串。

* 集合的值是唯一不可重复的。 

* 没有顺序。

* 第一个添加到集合的元素， 决定了创建集合时所使用的编码：

* Redis 内部是使用intset和 字典实现，所以这些操作的时间复习度都是O(1). 最方便是多个集合类型键之间可以进行并集，交集和差集运算。(ps: 灰常强大的喔~)


* SADD命令可以向集合添加一个新元素。和sets相关的操作也有许多，比如检测某个元素是否存在，以及实现交集，并集，差集等等。一例胜千言：
> 一个集合类型(set) 键可以至多为2^32 -1个。

<pre>
> sadd myset 1
(integer) 1
> sadd myset 2
(integer) 1
> sadd myset 3
(integer) 1

// 列出集合中的元素
> smembers myset
1) "1"
2) "2"
3) "3"

// 不能添加相同的元素
> sadd myset 3
(integer) 0

> smembers myset
1) "1"
2) "2"
3) "3"

// 删除元素
> SREM myset 2
"1"
> smembers myset
1) "1"
2) "3"

</pre>


#### 集合间运算
* 集合运算功能非常强大，可以实现很多实际需求。
* SDIFF  差集运算
* SINTER 交集运算
* SUNION 并集运算

<pre>
// SDIFF 差集运算

> SADD setB 2 3 4
(integer) 3
> SADD setA 1 2 3
(integer) 3
> SDIFF setA setB
1) "1"
> SDIFF setB setA
1) "4"

> SADD setC 2 3
(integer) 2

// 计算顺序是先计算setA - setB ,再计算结果与setC的差集。
> SDIFF setA setB setC
1) "1"


// SINTER 交集运算
> SINTER setA setB
1) "2"
2) "3"
> SINTER setA setB setC
1) "2"
2) "3"

// SUNION 并集
> SUNION setA setB
1) "1"
2) "2"
3) "3"
4) "4"
</pre>


### 有序集合
* 有序集合类型(sorted set) 的特点从它的名字就可以猜到。

* 在集合类型的基础上有序集合为集合中的每个元素都关联了一个分数，可通过获得分数最高或最低的前N个元素，或者获得指定分数范围内的元素等操作。

* 虽然集合内元素都是不同的，但它们的分数却可以相同。

<pre>
// 添加三个元素
> ZADD scoreboard 89 Tom 67 Peter 100 David
(integer) 3

// 发现Peter 的分数错了，修改分数
> ZADD scoreboard 76 Peter
(integer) 0

// 获得元素的分数
> ZSCORE scoreboard Tom
"89.0"

// 把著名黑客加入有序集合
> zadd hackers 1940 "Alan Kay" 1965 "Yukihiro Matsumoto" 1916 "Claude Shannon" 1969 "Linus Torvalds" 1912 "Alan Turing"
(integer) 5

// 顺序列出所有元素(从小到大)
> zrange hackers 0 -1
1) "Alan Turing"
2) "Claude Shannon"
3) "Alan Kay"
4) "Yukihiro Matsumoto"
5) "Linus Torvalds"

// 反转排序
> zrevrange hackers 0 -1
1) "Linus Torvalds"
2) "Yukihiro Matsumoto"
3) "Alan Kay"
4) "Claude Shannon"
5) "Alan Turing"

// 获取所有1950年之前出生的人。
> zrangebyscore hackers -inf 1950
1) "Alan Turing"
2) "Claude Shannon"
3) "Alan Kay"

// 删除生日介于1940到1960年之间的黑客。
zremrangebyscore hackers 1940 1960

</pre>

> 
一个非常重要的小贴士，ZSets只是有一个“默认的”顺序，但你仍然可以用 SORT 命令对有序集合做不同的排序（但这次服务器要耗费CPU了）。要想得到多种排序，一种可选方案是同时将每个元素加入多个有序集合。

#### 有序集合与列表
* 二者都是有序的。
* 二者都可以获得某一范围的元素。




## 持久化策略
### Redis提供了两种持久化策略，RDB和AOF。

* RDB是默认的，它定时创建数据库的完整磁盘镜像，即dump.rdb文件。创建镜像的时间间隔是可以设置的，假如每5分钟创建一次镜像，那么当系统崩溃时用户可能会丢失5分钟的数据。因此，RDB不是一个可靠性很高的方案，但是性能不错。RDB非常容易备份，用户直接将dump.rdb文件复制即可。

* 为了提供更好的可靠性，Redis支持AOF，即将操作写入日志中（appendonly.aof文件）。 AOF 就类似MYSQL的binlog. 

* 写日志的策略可以是每秒一次或每次操作一次，显然每秒一次意味着用户可能丢失1秒的数据，而每次操作一次的可靠性最高，但是性能最差。日志文件可能会增长到非常大，因此Redis后台会执行rewrite操作整理日志。AOF不适合备份。

* Redis推荐使用RDB，以及在需要可靠性的时候用RDB+AOF，不推荐单独使用AOF。Redis为了减少磁盘的负载，任何时刻都不会同时执行写镜像和写日志。

* Redis还提供主从同步的功能，可以为Redis配置一台slave，当master崩溃时，slave可以接管master的工作。

* 详情可参考Redis测试报告  http://my.oschina.net/fomy/blog/168399


## 一些测试数据
* 在8核 8G内存的服务器上,狂插140w条记录， 上面是redis，下面是httpsqs ,     redis比httpsqs快近一倍了
![](https://raw.github.com/wasabihu/ghost_export/master/post/img/redis/test1.jpg)


## Redis 常见问题和解决方法

#### 单台Redis的存放数据必须比物理内存小

* 一但内存用完，要使用到硬盘的情况，性能会很糟糕。

* 耗内存。尽管Redis对一些数据结构采用了压缩算法存储，但占用内存量还是过高。

#### Master写内存快照
* save命令调度rdbSave函数，会阻塞主线程的工作，当快照比较大时对性能影响是非常大的，会间断性暂停服务，所以Master最好不要写内存快照。

#### Master AOF持久化
* 如果不重写AOF文件，这个持久化方式对性能的影响是最小的，但是AOF文件会不断增大，AOF文件过大会影响Master重启的恢复速度。

#### Redis主从复制的性能问题
* 第一次Slave向Master同步的实现是：Slave向Master发出同步请求，Master先dump出rdb文件，然后将rdb文件全量传输给slave，然后Master把缓存的命令转发给Slave，初次同步完成。第二次以及以后的同步实现是：Master将变量的快照直接实时依次发送给各个Slave。

> 不管什么原因导致Slave和Master断开重连都会重复以上过程。Redis的主从复制是建立在内存快照的持久化基础上，只要有Slave就一定会有内存快照发生。虽然Redis宣称主从复制无阻塞，但由于Redis使用单线程服务，如果Master快照文件比较大，那么第一次全量传输会耗费比较长时间，且文件传输过程中Master可能无法提供服务，也就是说服务会中断，对于关键服务，这个后果也是很可怕的。
以上1.2.3.4根本问题的原因都离不开系统io瓶颈问题，也就是硬盘读写速度不够快，主进程 fsync()/write() 操作被阻塞。







## 一些关于NOSQL 的讨论
* [Nosql 中，很多人都说 Redis 性能比 Memcached 好？这是事实吗？有哪些网站采用 Redis，使用 Memcached 较出色的网站是哪些？](http://www.zhihu.com/question/19595880)

发表地址: [https://github.com/wasabihu/ghost_export/blob/master/post/redis.md](https://github.com/wasabihu/ghost_export/blob/master/post/redis.md)
