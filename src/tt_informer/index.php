<?php
$remont=0;
if ($remont==1) {phpinfo();} else {

if (isset($_GET['type'])){$type=$_GET['type'];}else{$type=0;}
$get_json=file_get_contents("http://the-tale.org/game/api/info?api_version=1.0&api_client=informer-1.0&account=".$_GET['id']);
$player_info=json_decode($get_json,true);

$name=$player_info['data']['account']['hero']['base']['name'];
$level=$player_info['data']['account']['hero']['base']['level'];
$race=$player_info['data']['account']['hero']['base']['race'];
$might=$player_info['data']['account']['hero']['might']['value'];
$might=intval($might);

switch($race){
case 0: $race_name='человек';$race_code='0';break;
case 1: $race_name='эльф';$race_code='1';break;
case 2: $race_name='орк';$race_code='2';break;
case 3: $race_name='гоблин';$race_code='3';break;
case 4: $race_name='дварф';$race_code='4';break;
}
$fontpath = realpath('.'); //replace . with a different directory if needed
putenv('GDFONTPATH='.$fontpath);
//FONT
$wrift="freeserif";
//FONT
if ($type==0) {
$dlina=150;
$wirina=110;
$im =imagecreate($dlina,$wirina);
//$im=imagecreatefrompng("template.png");
$back = ImageColorAllocate($im, 235, 235, 225);
$text = ImageColorAllocate($im, 56, 57, 58);
$textMight = ImageColorAllocate($im, 77, 44, 133);
$textLevel = ImageColorAllocate($im, 88, 88, 123);
$textHero = ImageColorAllocate($im, 90, 90, 123);
$textTitle = ImageColorAllocate($im, 14, 14, 99);
$ink = imagecolorallocate($im, 12, 23, 45);



	imagerectangle($im,0,0,$dlina-1,$wirina-1,$ink);
imagettftext($im, 13, 0, 10, 20, $textTitle, "/".$wrift.".ttf", "Мой герой: "); 
imagettftext($im, 11, 0, 10, 40, $textHero, "/".$wrift.".ttf", $name);
imagettftext($im, 11, 0, 10, 60, $textLevel, "/".$wrift.".ttf", $race_name." ".$level." уровня");
imagettftext($im, 11, 0, 10, 80, $textMight, "/".$wrift.".ttf", "могущество: ".$might);
imagettftext($im, 11, 0, 30, 105, $text, "/".$wrift.".ttf", "http://the-tale.org/");
}
if ($type==1) {
    $dlina=400;
	$wirina=30;
	$im = ImageCreate ( $dlina,$wirina);
	//$im=imagecreatefrompng("template.png");
	$back = ImageColorAllocate($im, 235, 235, 225);
	$text = ImageColorAllocate($im, 56, 57, 58);
	$textMight = ImageColorAllocate($im, 77, 44, 133);
	$textLevel = ImageColorAllocate($im, 88, 88, 123);
	$textHero = ImageColorAllocate($im, 70, 70, 103);
	$textTitle = ImageColorAllocate($im, 14, 14, 99);
	$ink = imagecolorallocate($im, 12, 23, 45);

	// st 4x
	imagerectangle($im,0,0,$dlina-1,$wirina-1,$ink);

	imagettftext($im, 11, 0, 10, 20, $textHero, "/".$wrift.".ttf", $name." - "); 
	$razmeri=imagettfbbox(11, 0, "/".$wrift.".ttf", $name);
	$next_pos=$razmeri[4];
	$stroka=$race_name." ".$level." уровня";
	imagettftext($im, 11, 0, $next_pos+25, 20, $textLevel, "/".$wrift.".ttf", $stroka);

	imagettftext($im, 11, 0, 315, 20, $text, "/".$wrift.".ttf", "the-tale.org");
}
if ($type==2) {
$dlina=150;
	$wirina=100;
	$im = ImageCreate ( $dlina,$wirina);
//$im=imagecreatefrompng("template.png");
$back = ImageColorAllocate($im, 235, 235, 225);
$text = ImageColorAllocate($im, 56, 57, 58);
$textMight = ImageColorAllocate($im, 77, 44, 133);
$textLevel = ImageColorAllocate($im, 88, 88, 123);
$textHero = ImageColorAllocate($im, 90, 90, 123);
$textTitle = ImageColorAllocate($im, 14, 14, 99);
$ink = imagecolorallocate($im, 12, 23, 45);


	imagerectangle($im,0,0,$dlina-1,$wirina-1,$ink);
imagettftext($im, 12, 0, 5, 20, $textTitle, "/".$wrift.".ttf", "Мой герой: "); 
imagettftext($im, 11, 0, 10, 40, $textHero, "/".$wrift.".ttf", $name); 
imagettftext($im, 11, 0, 10, 55, $textLevel, "/".$wrift.".ttf", $race_name." ".$level." уровня");
imagettftext($im, 11, 0, 10, 70, $textMight, "/".$wrift.".ttf", "могущество: ".$might);
imagettftext($im, 11, 0, 30, 90, $text, "/".$wrift.".ttf", "http://the-tale.org/");

}
if ($type==3) {
$dlina=150;
	$wirina=110;
$im=imagecreatefromjpeg("template.jpg");

$back = ImageColorAllocate($im, 235, 235, 225);
$text = ImageColorAllocate($im, 56, 57, 58);
$textMight = ImageColorAllocate($im, 77, 44, 133);
$textLevel = ImageColorAllocate($im, 102, 0, 51);

$textHero = ImageColorAllocate($im, 14, 14, 99);
$ink = imagecolorallocate($im, 12, 23, 45);


$symbols=iconv_strlen($name,"utf-8");
$levelInfo=$race_name." ".$level." уровня";
$symbols2=iconv_strlen($levelInfo,"utf-8");
if ($symbols>1) {$dat_size=13; $min_size=0;}
if ($symbols<7) {$dat_size=13; $min_size=-11;}
if ($symbols<8) {$dat_size=13; $min_size=-3;}
if ($symbols==8) {$dat_size=13; $min_size=5;}
if ($symbols>8) {$dat_size=12; $min_size=5;}
if ($symbols>10) {$dat_size=11; $min_size=7;}
if ($symbols>11) {$dat_size=10; $min_size=8;}
if ($symbols2<16) {$dat_padd=5;}else{$dat_padd=0;}
	imagerectangle($im,0,0,$dlina-1,$wirina-1,$ink);

imagettftext($im, $dat_size, 0, 35-($min_size), 24, $textHero, "/".$wrift.".ttf", $name); 
imagettftext($im, 12, 0, 10+$dat_padd, 45, $textLevel, "/".$wrift.".ttf", $levelInfo);
imagettftext($im, 10, 0, 15, 65, $textMight, "/".$wrift.".ttf", "могущество: ".$might);
imagettftext($im, 12, 0, 35, 95, $text, "/".$wrift.".ttf", "the-tale.org");
}
if ($type==4) {
    $dlina=400;
	$wirina=50;
	
	$im=imagecreatefromjpeg($race_code.".jpg");
	$back = ImageColorAllocate($im, 235, 235, 225);
	$text = ImageColorAllocate($im, 255, 255, 255);
	$textMight = ImageColorAllocate($im, 234, 214, 234);
	$textLevel = ImageColorAllocate($im, 255, 233, 211);
	$textHero = ImageColorAllocate($im, 233, 223, 199);
	$textTitle = ImageColorAllocate($im, 233, 233, 255);
	$ink = imagecolorallocate($im, 13, 26, 39);

	imagerectangle($im,0,0,$dlina-1,$wirina-1,$ink);
	
	imagettftext($im, 13, 0, 100, 21, $textHero, "/".$wrift.".ttf", $name." "); 
	imagettftext($im, 10, 0, 282, 37, $textHero, "/".$wrift.".ttf", "".$might." могущества"); 
	$razmeri=imagettfbbox(11, 0, "/".$wrift.".ttf", $name);
	$next_pos=$razmeri[4];
	$stroka=$race_name." ".$level." уровня";
	imagettftext($im, 11, 0, 102, 37, $textLevel, "/".$wrift.".ttf", $stroka);

	imagettftext($im, 11, 0, 315, 21, $text, "/".$wrift.".ttf", "the-tale.org");
}
/** 
* $fontsize - размер шрифта 
* 0 - угол наклона 
* $coord_x - координата х 
* $coord_y - координата у 
* $text_color - цвет шрифта (получаем от функции imgecolorallocate()) 
* $font_path - шрифт
*/ 
header("Cache-Control: max-age=86400");
header('Content-type: image/png');
ImagePng ($im);

//cleanup
ImageDestroy ($im);
}
?>