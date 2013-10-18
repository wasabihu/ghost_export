## 介绍
* redis是开源的内存数据库，很容易下载源码，编译也很直接。
* redis自带了服务器和客户端，使用src/redis-server可以运行服务器，默认端口是6379，redis.conf有很多配置选项。
* 可以用src/redis-cli测试一下服务器是否正常，-h指定服务器ip，redis提供了较多的命令， 比如set、put、append、dbsize等。

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

### Redis 集合
* Redis集合是未排序的集合，其元素是二进制安全的字符串。
* SADD命令可以向集合添加一个新元素。和sets相关的操作也有许多，比如检测某个元素是否存在，以及实现交集，并集，差集等等。一例胜千言：
<pre>
$ redis-cli sadd myset 1
(integer) 1
$ redis-cli sadd myset 2
(integer) 1
$ redis-cli sadd myset 3
(integer) 1
$ redis-cli smembers myset
1. 3
2. 1
3. 2
</pre>

## AAAAAAAAAAa