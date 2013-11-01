
## Hello World
* ng-app 
* ng-model=“yourName”
* {{ yourName }}
* ng-controller

* 如果一个应用会掌控整个页面，那么你就可以把ng-app指令直接写在html元素上。

* ng-controller指令给所在的DOM元素创建了一个新的$scope 对象，并将这个$scope 对象包含进外层DOM元素的$scope 对象里。

## Scopes 
* $scope是一个把view（一个DOM元素）连结到controller上的对象。在我们的MVC结构里，这个 $scope 将成为model，它提供一个绑定到DOM元素（以及其子元素）上的excecution context。








## 参考资料
* [七步从Angular.JS菜鸟到专家（1）](http://blog.jobbole.com/46779/)