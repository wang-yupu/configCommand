
# configCommand / cfgcmd

在游戏内使用MCDR命令修改其它插件/Mod的配置！

## 命令

- `!!cfg env <路径，以MCDR根路径开始，可用绝对/相对路径> <配置文件> [可选: 读写器类型]`: 将执行者修改的目标文件设置为对应文件
- `!!cfg quit`: 清空执行者的目标文件
- `!!cfg write`: 写入目标文件
- `!!cfg reload`: 重载目标文件(会覆盖已经进行的所有修改)
- `!!cfg info`: 查看文件信息

---  

- `!!cfg set <key> <value>`: 设置键值对，`<key>`中`.`分割的键将被当做配置树的路径解释(具体见下文示例)，此命令的`key`不支持`..`此类相对路径
- `!!cfg rm <key>`: 删除键对应的内容
- `!!cfg mv <sourceKey> <destKey>`: 移动，也可以当重命名使用
- `!!cfg cp <sourceKey> <destKey>`: 复制粘贴
- `!!cfg cd <key>`: 因为配置文件是树状结构，所以就提供一个类似文件系统操作的`cd`指令。在读写器为`plain`时不可用
- `!!cfg ls [可选: page]`: 查看当前Object内容。在读写器为`plain`时打印全文。每10行算一页
- `!!cfg lsDir <路径>`: 以MCDR目录为根目录查看文件列表

---  

> 执行`!!cfg env ...`后，不会占用文件  
> 执行`!!cfg info`给出当前文件信息  
> 执行`!!cfg ls`打印指针所在Object的内容  
> 读写器根据文件后缀名判断。没有后缀名或者未知后缀名的会选择使用`plain`读写器  
> 若读写器为`plain`，`<key>`参数指定的就是行号  
> 若`<key>`包含空格且后面还有参数，用英文双引号把它括住。用`\`可以转义。具体见[QuotableText](https://docs.mcdreforged.com/zh-cn/latest/code_references/command.html#mcdreforged.command.builder.nodes.arguments.QuotableText)  
> `set`子命令对于`value`类型的判断: 若存在字符，则是字符串；若以双引号括住且只有数字，则是字符串；未被双引号括住且只有数字，则是数字；若只给出了`key`，则`value`是None  

### 示例

原始配置文件:

```json
1  {
2      "foo": 123,
3      "bar": {
4          "barFoo": "?",
5          "barBar": {
6              "barBarFoo": 456
7          }
8      },
9      "buzz": [
10         "wangyupu","zzfx1166"
11     ]
12 }
```

命令(有顺序):

1. `!!cfg env "config/foo/" bar.json`: 打开文件
2. `!!cfg set foo 1231`: 设置第2行的值为1231
3. `!!cfg set bar.barFoo "!"`: 设置第4行的值为"!"
4. `!!cfg rm buzz.1`: 删除第10行列表的第二项 (0-based index)
5. `!!cfg cd bar.barBar`: 切换目前指针到第5行的Object
6. `!!cfg set barBarFoo 789`: 修改第6行的值为789
7. `!!cfg write`: 写入文件
8. `!!cfg quit`: 离开文件

修改后配置文件:

```json
1  {
2      "foo": 1231,
3      "bar": {
4          "barFoo": "!",
5          "barBar": {
6              "barBarFoo": 789
7          }
8      },
9      "buzz": [
10         "wangyupu"
11     ]
12 }
```

## 插件配置

```yaml
ownerPlayer: 玩家名称
cfgCmdPermission: 4
```

## 支持的配置文件格式

- `json`
- `yaml`(`yml`)
- `toml`
- 纯文本
