#!/usr/bin/perl

#----------------------------------------------------
#ParaFla用サンプル 簡易ランキングシステム ver5 by D4U
#----------------------------------------------------
#------------------------------
#設定部…必要に応じて書きかえる
#------------------------------
#ランキングデータのファイル名
$datafile = "ranking.dat";

#ソート基準:1の時降順(得点が多いほど上位)になる 逆の場合は0にすること
$sortc = 1;

#同名排他:1にするとランキングの中に同じ名前が複数存在しない
$domei = 0;

#記録数:5ならば1~5位までが記録される
$max = 100;

#通信用パスワード
$password = "trimeresurus";

#------------------------------------------------
#以下実行部…意味がわからない部分はいじらないこと
#------------------------------------------------
require './jcode.pl';
print "Content-type: \n\n";
$maxp = $max + 1;

#(データファイル再構築モード)
if ($ENV{'QUERY_STRING'} eq $password){
	&indata;
	&outdata;
	print "$datafileを作成しました";
	exit;
}

#(渡されたデータの解釈)
read(STDIN,$buffer,$ENV{'CONTENT_LENGTH'});

@pairs = split(/&/,$buffer);
foreach $pair (@pairs) {
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	&jcode'convert(*value,'sjis');
	$DATA{$name} = $value;
}
$name[$maxp] = $DATA{'name'};
$score[$maxp] = $DATA{'score'} + 0;
$myname = $name[$maxp];
@t = split(/\//,$myname);
$myrname = @t[0];
$rname[$maxp] = @t[0];
$myscore = $score[$maxp];

#(パスワードチェック)
if ($DATA{'pass'} ne $password) { $result = -4; &tarm; exit;}

#(データが正しく渡されているかのチェック)
if ($name[$maxp] eq "" || $score[$maxp] == 0) { $result = -3; &tarm; exit;}

#(データファイルの存在確認)
if (!open(IN,"$datafile")) { $result = -1; &tarm; exit;}

&indata;

#(データが壊れていないかのチェック)
if ($name[1] eq "" && $score[1] == 0) { $result = -2; &tarm; exit;}

#(同名の確認)
if ($domei == 1){
	$same = "";
	for ($i=1; $i<=$max; $i++){
		if ($rname[$i] eq $rname[$maxp]){ $same = $rname[$i]; last;}
	}
}

#(データの並べかえ)
$myrank = $maxp;
for ($i=$max; $i>=1; $i--){
	$change = 0;
	if ($sortc eq 1 && $score[$i] < $score[$i+1]) { $change = 1;}
	if ($sortc ne 1 && $score[$i] > $score[$i+1]) { $change = 1;}

	if ($change eq 1){
		($name[$i],$name[$i+1]) = ($name[$i+1],$name[$i]);
		($rname[$i],$rname[$i+1]) = ($rname[$i+1],$rname[$i]);
		($score[$i],$score[$i+1]) = ($score[$i+1],$score[$i]);
		$myrank--;
	}
}

#(同名の排除)
if ($same ne ""){
	for ($i=$maxp; $i>=1; $i--){
		if ($same eq $rname[$i]) { last;}
	}
	if ($i != $maxp){
		for ($j=$i; $j<=$max; $j++){
			$name[$j] = $name[$j+1];
			$rname[$j] = $rname[$j+1];
			$score[$j] = $score[$j+1];
		}
	}
	$myrank = $maxp;
	for ($i=1; $i<=$max; $i++){
		if ($rname[$i] eq $myrname && $score[$i] == $myscore)
			{ $myrank = $i; last;}
	}
}

if ($myrank == $maxp) { $result = -5; &tarm; exit;}

&outdata;

$result = $myrank;
&tarm; exit;

#(サブルーチン:データファイルの読み込み)
sub indata {
	open(IN,"<$datafile");
	flock(IN,2);
	$indat = <IN>;
	close(IN);
	flock(IN,8);

	@pairs = split(/&/,$indat);
	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		&jcode'convert(*value,'sjis');
		$DATA{$name} = $value;
	}

	for ($i=1; $i<=$max; $i++){
		$name[$i] = $DATA{"name$i"};
		@t = split(/\//,$name[$i]);
		$rname[$i] = @t[0];
		$score[$i] = $DATA{"score$i"} + 0;
	}
}

#(サブルーチン:データファイルの書き込み)
sub outdata{
	$buf = ""; $buf2 = "ardata=";
	for ($i=1; $i<=$max; $i++){
		$buf .= "name$i\=$name[$i]\&score$i\=$score[$i]\&";
		$buf2 .= "$name[$i]\,$score[$i]\:";
	}
	$buf .= $buf2;
	open(OT,">$datafile");
	flock(OT,2);
	print OT $buf;
	close(OT);
	flock(OT,8);
}

#(サブルーチン：終了処理)
sub tarm {
	print "result=$result";
}

#変数resultに返される値
# 0   : 予期しないエラー
# 1~n : 1位~n位に登録された(データファイルは更新された)
# -1  : データファイルが見つからなかったので中止した
# -2  : データファイルの内容がおかしいので中止した
# -3  : CGIに渡したデータがおかしい(名前が無いか、得点が0)ので中止した
# -4  : 通信パスワードが違うので中止した
# -5  : ランク外だった
