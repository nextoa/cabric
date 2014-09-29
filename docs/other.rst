

#其他文件的安装问题,安装常用的include
#xcode-select --install


* 改变 xml 的lib


# 没敢测试
#pcre-config --libs --cflags
#-L/usr/lib -lpcre
#-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/usr/include/libxml2

#locate xmlversion.h


sudo C_INCLUDE_PATH=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/usr/include/libxml2 pip install pyquery



