### empty和isset 的坑
* 下面两段代码,同样会导致PHP解析错误,也就是一个致命错误.
*  php5.3开始才会报错, 错误像这样子:
> Fatal error: Can't use function return value in write context in \xxx\user.php on line 1651

* 原因,PHP手册上有说:

> 因为是一个语言构造器而不是一个函数，不能被 可变函数 调用。 
empty() 只检测变量，检测任何非变量的东西都将导致解析错误。换句话说，后边的语句将不会起作用： empty(addslashes($name))。 

<pre>
        $var ='';
        if(empty(strval($var)) ){
            echo "BBBBBBBBBB";
        }
        
        if(isset(strval($var)) ){
            echo "BBBBBBBBBB";
        }
</pre>