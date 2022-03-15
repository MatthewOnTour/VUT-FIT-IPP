<?php
#IPP projekt 1   parse.php
#created by: Matus Justik
#login: xjusti00

$firstLineHeader = false;      #pomocna premena na kontrolu hlavicky suboru


#error 10 chybajuci parameter skriptu alebo pouzitie zakazanej kombinacie
#error 11 chyba pri otvarani vstupnich suborov
#error 12 chyba pri otvarani vystupnych suborov
#error 21 chybna alebo chybajuca hlavicka v zdrojovom kode
#error 22 neznamy alebo chybny operacny kod v zdrojovom kode
#error 23 ina lexikalna alebo syntakticka chyba zdrojoveho kodu
#error 99 interna chyba 

ini_set('display_errors', 'stderr');

if ($argc > 1) {                         #pripadny help

    if ($argv[2] = "--help") {
        echo ("Pouzitie: parse.php [prikaz] < vstupnySubor \n");
        exit(0);
    }
}

#start xml
$xml = new XMLWriter();
$xml->openURI('php://output');
$xml->startDocument('1.0', 'UTF-8');
$xml->setIndent(4);
$xml->startElement('program');
$xml->writeAttribute('language', 'IPPcode22');

#zaciatok funkcii
function none($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    $xml->endElement();
}
function varsym($xml, $chopLine, $order)
{

    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    $xml->writeAttribute('type', 'var');
    #kontrola spravnosti premennej
    if (!preg_match("/^(GF@|LF@|TF@)/", $chopLine[1])) {
        fwrite(STDERR, "Chyba premennej \n");
        exit(23);
    }
    $xml->text($chopLine[1]);
    $xml->endElement();
    #argument 2
    $xml->startElement('arg2');
    #o co sa jedna
    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[2]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[2])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(int@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(bool@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[2]) && (preg_match_all('/\\\\/', $chopLine[2]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[2])))) {
        $chopLine[2] = preg_replace("/^(string@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(nil@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna\n");
        exit(23);
    }

    $xml->text($chopLine[2]);
    $xml->endElement();
    $xml->endElement();
}

function varsymsym($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    $xml->writeAttribute('type', 'var');
    #kontrola spravnosti premennej
    if (!preg_match("/^(GF@|LF@|TF@)/", $chopLine[1])) {
        fwrite(STDERR, "Chyba premennej \n");
        exit(23);
    }
    $xml->text($chopLine[1]);
    $xml->endElement();
    #argument 2
    $xml->startElement('arg2');
    #o co sa jedna
    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[2]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[2])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(int@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(bool@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[2]) && (preg_match_all('/\\\\/', $chopLine[2]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[2])))) {
        $chopLine[2] = preg_replace("/^(string@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(nil@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna symb1\n");
        exit(23);
    }
    $xml->text($chopLine[2]);
    $xml->endElement();


    #argument 3
    $xml->startElement('arg3');

    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[3]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[3])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(int@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(bool@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[3]) && (preg_match_all('/\\\\/', $chopLine[3]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[3])))) {
        $chopLine[3] = preg_replace("/^(string@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(nil@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna symb2\n");
        exit(23);
    }
    $xml->text($chopLine[3]);
    $xml->endElement();
    $xml->endElement();
}

function variable($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    $xml->writeAttribute('type', 'var');
    #kontrola spravnosti premennej
    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[1]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[1])) {
        $xml->text($chopLine[1]);
        $xml->endElement();
        $xml->endElement();
    } else {
        fwrite(STDERR, "Chyba premennej \n");
        exit(23);
    }
}

function lab($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    if (preg_match("/^[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[1])) {
        $xml->startElement('arg1');
        $xml->writeAttribute('type', 'label');
        $xml->text($chopLine[1]);
    } else {
        fwrite(STDERR, "Chyba \n");
        exit(23);
    }

    $xml->endElement();
    $xml->endElement();
}

function symbol($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[1]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[1])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[1])) {
        $chopLine[1] = preg_replace("/^(int@)/", "", $chopLine[1]);                      #odstranenie toho co netreba !!!!!!!!!!!!!!!!!!!!!!
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[1])) {
        $chopLine[1] = preg_replace("/^(bool@)/", "", $chopLine[1]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[1]) && (preg_match_all('/\\\\/', $chopLine[1]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[1])))) {
        $chopLine[1] = preg_replace("/^(string@)/", "", $chopLine[1]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[1])) {
        $chopLine[1] = preg_replace("/^(nil@)/", "", $chopLine[1]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna\n");
        exit(23);
    }
    $xml->text($chopLine[1]);
    $xml->endElement();
    $xml->endElement();
}

function labsymsym($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    $xml->writeAttribute('type', 'label');
    $xml->text($chopLine[1]);
    $xml->endElement();
    #argument 2
    $xml->startElement('arg2');
    #o co sa jedna
    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[2]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[2])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(int@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(bool@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[2]) && (preg_match_all('/\\\\/', $chopLine[2]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[2])))) {
        $chopLine[2] = preg_replace("/^(string@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[2])) {
        $chopLine[2] = preg_replace("/^(nil@)/", "", $chopLine[2]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna symb1\n");
        exit(23);
    }
    $xml->text($chopLine[2]);
    $xml->endElement();


    #argument 3
    $xml->startElement('arg3');

    if (preg_match("/^(GF@|LF@|TF@)(?!@)/", $chopLine[3]) && preg_match("/@[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/", $chopLine[3])) {
        $xml->writeAttribute('type', 'var');
    } elseif (preg_match("/^(int@[+-]?[0-9]+$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(int@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'int');
    } elseif (preg_match("/^(bool@(true|false)$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(bool@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'bool');
    } elseif (preg_match("/^(string@(?:[^\s\#]|(\[0-9]{3}))*$)/", $chopLine[3]) && (preg_match_all('/\\\\/', $chopLine[3]) === (preg_match_all('/\\\\[0-9]{3}/', $chopLine[3])))) {
        $chopLine[3] = preg_replace("/^(string@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'string');
    } elseif (preg_match("/^(nil@nil$)/", $chopLine[3])) {
        $chopLine[3] = preg_replace("/^(nil@)/", "", $chopLine[3]);
        $xml->writeAttribute('type', 'nil');
    } else {
        fwrite(STDERR, "zle zadana premenna symb2\n");
        exit(23);
    }
    $xml->text($chopLine[3]);
    $xml->endElement();
    $xml->endElement();
}

function vartype($xml, $chopLine, $order)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order);
    $xml->writeAttribute('opcode', $chopLine[0]);
    #argument 1
    $xml->startElement('arg1');
    $xml->writeAttribute('type', 'var');
    #kontrola spravnosti premennej
    if (!preg_match("/^(GF@|LF@|TF@)/", $chopLine[1])) {
        fwrite(STDERR, "Chyba premennej \n");
        exit(23);
    }
    $xml->text($chopLine[1]);
    $xml->endElement();
    #argument 2
    if (preg_match("/^(string|bool|int|nil)$/", $chopLine[2])) {
        $xml->startElement('arg2');
        $xml->writeAttribute('type', 'type');
        $xml->text($chopLine[2]);
        $xml->endElement();
    } else {
        fwrite(STDERR, "Chyba premennej \n");
        exit(23);
    }
    $xml->endElement();
}


$order = 1;
#nacitanie suboru ... jednotlivych riadkov 
while ($line = fgets(STDIN)) {

    #riesenie komentarov
    $line = preg_replace("/#.*/", "", $line);
    $line = trim($line);
    if ($line == "") {

        continue;
    }

    $line = preg_replace('/^\s+|\s+$/', '', $line); #odstranenie neziaducich znakov

    #kontrola hlavicky suboru
    if (!$firstLineHeader) {
        if (!strcmp($line, ".IPPcode22")) {
            $firstLineHeader = true;
            continue;
        } else {
            fprintf(STDERR, "Nespravna hlavicka suboru\n");
            exit(21);
        }
    }

    #rozdelenie line na chopLine
    $chopLine = preg_split('/\s+/', trim($line, "\n"));

    #prve slovo da na velke znaky
    $chopLine[0] = strtoupper($chopLine[0]);

    switch ($chopLine[0]) {



        case 'MOVE':
            if (count($chopLine) == 3) {
                varsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia MOVE -> MOVE ⟨var⟩ ⟨symb⟩ \n");
                exit(23);
            }

            break;
        case 'CREATEFRAME':
            if (count($chopLine) == 1) {
                none($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia CREATEFRAME \n");
                exit(23);
            }


            break;
        case 'PUSHFRAME':
            if (count($chopLine) == 1) {
                none($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia PUSHFRAME \n");
                exit(23);
            }
            break;
        case 'POPFRAME':
            if (count($chopLine) == 1) {
                none($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia POPFRAME \n");
                exit(23);
            }
            break;
        case 'DEFVAR':
            if (count($chopLine) == 2) {
                variable($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia DEFVAR -> DEFVAR ⟨var⟩ \n");
                exit(23);
            }

            break;
        case 'CALL':
            if (count($chopLine) == 2) {
                lab($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia CALL -> CALL ⟨label⟩ \n");
                exit(23);
            }
            break;
        case 'RETURN':
            if (count($chopLine) == 1) {
                none($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia RETURN \n");
                exit(23);
            }
            break;
        case 'PUSHS':
            if (count($chopLine) == 2) {
                symbol($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia PUSHS -> PUSHS ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'POPS':
            if (count($chopLine) == 2) {
                variable($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia POPS -> POPS ⟨var⟩ \n");
                exit(23);
            }
            break;
        case 'ADD':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia ADD -> ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'SUB':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia SUB -> SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'MUL':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia MUL -> MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'IDIV':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia IDIV -> IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'LT':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia LT/GT/EQ -> LT/GT/EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'GT':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia LT/GT/EQ -> LT/GT/EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'EQ':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia LT/GT/EQ -> LT/GT/EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'AND':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia AND/OR/NOT -> AND/OR/NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'OR':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia AND/OR/NOT -> AND/OR/NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'NOT':
            if (count($chopLine) == 3) {
                varsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia AND/OR/NOT -> AND/OR/NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ -> NOT ma len 2 operandy ⟨var⟩ ⟨symb⟩\n");
                exit(23);
            }
            break;
        case 'INT2CHAR':
            if (count($chopLine) == 3) {
                varsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia INT2CHAR -> INT2CHAR ⟨var⟩ ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'STRI2INT':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia STRI2INT -> STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'READ':
            if (count($chopLine) == 3) {
                vartype($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia READ -> READ ⟨var⟩ ⟨type⟩ \n");
                exit(23);
            }
            break;
        case 'WRITE':
            if (count($chopLine) == 2) {
                symbol($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia WRITE -> WRITE ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'CONCAT':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia CONCAT -> CONCAT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'STRLEN':
            if (count($chopLine) == 3) {
                varsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia STRLEN -> STRLEN ⟨var⟩ ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'GETCHAR':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia GETCHAR -> GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'SETCHAR':
            if (count($chopLine) == 4) {
                varsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia SETCHAR -> SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'TYPE':
            if (count($chopLine) == 3) {
                varsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia TYPE -> TYPE ⟨var⟩ ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'LABEL':
            if (count($chopLine) == 2) {
                lab($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia LABEL -> LABEL ⟨label⟩ \n");
                exit(23);
            }
            break;
        case 'JUMP':
            if (count($chopLine) == 2) {
                lab($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia JUMP -> JUMP ⟨label⟩ \n");
                exit(23);
            }
            break;
        case 'JUMPIFEQ':
            if (count($chopLine) == 4) {
                labsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia JUMPIFEQ -> JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'JUMPIFNEQ':
            if (count($chopLine) == 4) {
                labsymsym($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia JUMPIFNEQ -> JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩ \n");
                exit(23);
            }
            break;
        case 'EXIT':
            if (count($chopLine) == 2) {
                symbol($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia EXIT -> EXIT ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'DPRINT':
            if (count($chopLine) == 2) {
                symbol($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia DPRINT -> DPRINT ⟨symb⟩ \n");
                exit(23);
            }
            break;
        case 'BREAK':
            if (count($chopLine) == 1) {
                none($xml, $chopLine, $order);
            } else {
                fprintf(STDERR, "nespravne zadana instrukcia BREAK \n");
                exit(23);
            }
            break;

        default:



            fprintf(STDERR, "nespravna instrukcia \n");
            exit(22);


            break;
    }
    $commentFlag = false;
    $order++;
}

#koniec xml
$xml->endElement();
$xml->endElement();
$xml->endDocument();