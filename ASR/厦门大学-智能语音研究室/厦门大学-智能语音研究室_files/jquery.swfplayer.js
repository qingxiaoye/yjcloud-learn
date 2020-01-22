/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
//document.write('<script type="text/javascript" src="' + '' + '/_test/flexpaper2/flexpaper.css"></script>');
//document.write('<script type="text/javascript" src="' + '' + '/_test/flexpaper2/jquery.extensions.min.js"></script>');
//document.write('<script type="text/javascript" src="' + '' + '/_test/flexpaper2/flexpaper_handlers.js"></script>');

var context = "";
var localeChain = "zh_CN";
$("script[sudy-wp-context]").each(function(i) {
    context = $(this).attr("sudy-wp-context");
    if (context) {
        context = "/" + context;
    }
});
var fls = flashChecker();
if (/Android|Windows Phone|webOS|iPhone|iPod|iPad|BlackBerry/i.test(navigator.userAgent)) {
    fls.f = 0;
//    localeChain = "en_US";
}
if (fls.f === 0) {
    document.write('<script type="text/javascript" src="' + '' + '/_js/_portletPlugs/swfPlayer/flexpaper2/flexpaper.js"></script>');
}
$().ready(function() {
//        document.write("您安装了flash,当前flash版本为: " + fls.v + ".x");
    $("a[sudy-wp-player]").each(function(i) {
        var _href = $(this).attr("href");
        var _sudyvideoplayersrc = $(this).attr("sudy-wp-player");
        _href = _href.substring(0, _href.lastIndexOf("/") + 1) + _sudyvideoplayersrc;
        if (swfPlayer(_href) !== null) {
            var prev = $($(this)).prev("img[src*=icon");
            $($(this)).replaceWith("<div id=\"" + Math.random() + "\" swsrc=\"" + _href + "\" pdfsrc=\"" + $(this).attr("href") + "\" class=\"wp_pdf_player\" sudyplayer=\"wp_pdf_player\"></div>");
            if (prev) {
                prev.remove();
            }
        } else if (!jsPlayer(_href)) {
            $(this).attr("href", _href);
        }
    });
    $(".wp_pdf_player,div[sudyplayer='wp_pdf_player'],img[sudyplayer='wp_pdf_player']").each(function(i) {
        if (!$(this).attr("class")) {
            $(this).css("width", "100%");
            $(this).css("height", "700px");
        }
        if(!$(this).attr("class")){
            $(this).attr("class",$(this).attr("sudyplayer"));
        }
        var id = $(this).attr("id");
        var swfsrc = $(this).attr("swsrc");
        var pdfsrc = $(this).attr("pdfsrc");
        var flexpaper = context + "/_js/_portletPlugs/swfPlayer/flexpaper/FlexPaper_flash/FlexPaperViewer";
        var uuid = Math.random().toString();
        var sudy_wp_player = $(this).attr("sudy-wp-player");
        if ($(this)[0].tagName == "IMG") {
            $($(this)).replaceWith("<div id=\"" + id + "\" swsrc=\"" + swfsrc + "\" pdfsrc=\"" + pdfsrc + "\" class=\"wp_pdf_player\" sudyplayer=\"wp_pdf_player\"></div>");
        }
        /**
         * 如果本地安装了flash则用原来的方式播放,如果没有安装flash则使用新的方式播放
         */
        if (fls.f) {
            new FlexPaperViewer(flexpaper, id, {config: {
                    SwfFile: escape(swfsrc + "?src=" + pdfsrc + "&t=" + uuid),
                    Scale: 1.0,
                    ZoomTransition: "easeOut",
                    ZoomTime: 0.5,
                    ZoomInterval: 0.2,
                    FitPageOnLoad: false,
                    FitWidthOnLoad: true,
                    FullScreenAsMaxWindow: false,
                    ProgressiveLoading: false,
                    MinZoomSize: 0.2,
                    MaxZoomSize: 5,
                    SearchMatchAll: false,
                    InitViewMode: "Portrait",
                    PrintPaperAsBitmap: false,
                    ViewModeToolsVisible: true,
                    ZoomToolsVisible: true,
                    NavToolsVisible: true,
                    CursorToolsVisible: false,
                    SearchToolsVisible: false,
                    localeChain: localeChain
                }});
        } else {
            var pdfUrl = pdfsrc.substring(0, pdfsrc.lastIndexOf("/"));
            var pdfName = pdfsrc.substring(0, pdfsrc.lastIndexOf("."));
            var sudyImgLen = 0;
            $.ajax({
                url: document.location.protocol+"//" + location.host + pdfName + ".json",
                type: 'get',
                data: '',
                dataType: 'json',
                async:false,
                success: function(data) {
                    try{
                        sudyImgLen = data[0].pdfImgLen;
                    }catch(e){
                        sudyImgLen = 0;
                    }
                },
                error: function(res) {
                    sudyImgLen = 0;
                }

            });
            if (sudyImgLen > 0) {
                var _data = "[";
                for (var i = 0; i < sudyImgLen; i++) {
                    _data += "{\"src\": \"" + pdfName + "_" + (i + 1) + ".png" + "\",\"width\":\"100\",\"height\": \"100\"}";
                    if (i < (sudyImgLen - 1)) {
                        _data += ",";
                    }
                }
                _data += "]";
                $(this).html("<div data-data='{\"img\":" + _data + "}' class=\"pictureswitch\" data-PictureSwitch  data-src='{\"url\":\"data.json\"}'></div>");
                pictureViewer(context);
            } else {
//                var flexPaperViewer = new FlexPaperViewer("FlexPaperViewer", id, {config: {
//                        IMGFiles: pdfName + '_{page}.png',
//                        JSONFile: pdfUrl + "/" + $(this).attr("sudy-wp-player"),
//                        PDFFile: pdfsrc,
//                        Scale: 1.0,
//                        ZoomTransition: "easeOut",
//                        ZoomTime: 0.5,
//                        ZoomInterval: 0.2,
//                        FitPageOnLoad: false,
//                        FitWidthOnLoad: true,
//                        FullScreenAsMaxWindow: false,
//                        ProgressiveLoading: false,
//                        MinZoomSize: 0.2,
//                        MaxZoomSize: 5,
//                        SearchMatchAll: false,
//                        InitViewMode: "Portrait",
//                        RenderingOrder: 'html,flash',
//                        PrintPaperAsBitmap: false,
//                        ViewModeToolsVisible: true,
//                        ZoomToolsVisible: true,
//                        NavToolsVisible: true,
//                        CursorToolsVisible: false,
//                        SearchToolsVisible: false,
//                        jsDirectory: context + '/_js/_portletPlugs/swfPlayer/flexpaper2/js-adaptive/',
//                        localeDirectory: context + '/_js/_portletPlugs/swfPlayer/flexpaper2/locale/',
//                        localeChain: localeChain
//                    }});
            }
        }
    });
});
function swfPlayer(url) {
    var r, re;
    re = /.(swf)$/i;
    r = url.match(re);
    return r;
}
function jsPlayer(url) {
    var r, re;
    re = /.(js)$/i;
    r = url.match(re);
    return r;
}
function flashChecker() {
    var hasFlash = 0; //是否安装了flash 
    var flashVersion = 0; //flash版本 
    if (document.all) {
        var swf = new ActiveXObject('ShockwaveFlash.ShockwaveFlash');
        if (swf) {
            hasFlash = 1;
            VSwf = swf.GetVariable("$version");
            flashVersion = parseInt(VSwf.split(" ")[1].split(",")[0]);
        }
    } else {
        if (navigator.plugins && navigator.plugins.length > 0) {
            var swf = navigator.plugins["Shockwave Flash"];
            if (swf) {
                hasFlash = 1;
                var words = swf.description.split(" ");
                for (var i = 0; i < words.length; ++i) {
                    if (isNaN(parseInt(words[i])))
                        continue;
                    flashVersion = parseInt(words[i]);
                }
            }
        }
    }
    return {
        f: hasFlash,
        v: flashVersion
    };
}


