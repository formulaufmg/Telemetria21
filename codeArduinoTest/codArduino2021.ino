
byte buffer1[20];
byte buffer2[36];
byte buffer3[34];
byte buffer4[46];
int a, b, c;
 int i = 0;
  int j = 255;
int k = 0, aux ;


/*Variaveis globais dos dados*/
uint32_t TIMERCOUNT=0;

/*Flag do Beacon*/
uint8_t BEACON_FLAG = 0;

/*Variáveis do Pacote 1 -> 60Hz*/
uint16_t acelX = 0, //Aceleração no eixo X da placa dianteira esquerda
     acelY = 0, //Aceleração no eixo Y da placa dianteira esquerda
     acelZ = 0, //Aceleração no eixo Z da placa dianteira esquerda
     velAng = 0,   //velocidade angular
     vel_DE = 0,   //Velocidade da roda dianteira esquerda
     vel_DD = 0,   //Velocidade da roda dianteira direita
     vel_TE = 0,   //Velocidade da roda traseira esquerda
     vel_TD = 0,   //Velocidade da roda traseira direita
     RPM = 0,
     Beacon = 0;

/*Variáveis do Pacote 2 -> 30Hz*/
uint32_t ext1 = 0, //Extensômetro 1 da placa dianteira esquerda
       ext2 = 0, //Extensômetro 2 da placa dianteira esquerda
       ext3 = 0, //Extensômetro 3 da placa dianteira esquerda
       ext4 = 0, //Extensômetro 1 da placa dianteira direita
       ext5 = 0, //Extensômetro 2 da placa dianteira direita
       ext6 = 0, //Extensômetro 3 da placa dianteira direita
       ext7 = 0, //Extensômetro 1 da placa traseira esquerda
       ext8 = 0, //Extensômetro 2 da placa traseira esquerda
       ext9 = 0, //Extensômetro 3 da placa traseira esquerda
       ext10 = 0; //Extensômetro 1 da placa traseira dianteira

/*Variáveis do Pacote 3 -> 30Hz*/
uint16_t TPS = 0,       //TPS
     OILP = 0,      //Pressão de Óleo
     FUELP = 0,     //Pressão de Combustível
     VAZBICOS = 0,    //Vazão dos Bicos
     PoSus_DE = 0,    //Posição da suspensão da placa dianteira esquerda
     PoSus_DD = 0,    //Posição da suspensão da placa dianteira direita
     PoSus_TE = 0,    //Posição da suspensão da placa traseira esquerda
     PoSus_TD = 0,    //Posição da suspensão da placa traseira dianteira
     PosVolante = 0,  //Posição do volante
     BatCor = 0,    //Corrente da Bateria
     VentCor = 0,     //Corrente da Ventoinha
     BombCor = 0,     //Corrente da Bomba
     PresFreio_D = 0,   //Pressão do Freio Dianteiro
     PresFreio_T = 0;   //Pressão do Freio Traseiro

/*Variáveis do Pacote 4 -> 10Hz*/
uint16_t BAT = 0,
     ECT = 0,
     OILT = 0,
     Tempdisco_DE = 0,
     Tempdisco_DD = 0,
     Tempdisco_TE = 0,
     Tempdisco_TD = 0,
     TempVentoinha = 0,
     TempBomba = 0,
     TempBat = 0,
     PosRunners = 0,
     AcioVent = 0,
     AcioBomba = 0,
     AcioSpark = 0,
     AcioMata = 0;
uint32_t GPS_Lat = 0, //GPS.lat*100;
     GPS_Long = 0; //GPS.long*100;
char  GPS_NS = 'N',
     GPS_EW = 'E',
     hgpshour = 0,
     hgpsminute = 0,
     hgpsseconds = 0,
     hgpsmilliseconds = 0,
     hgpsyear = 0,
     hgpsmonth = 0,
     hgpsday;


void setup() {

    
   Serial.begin(115200);
   delay(100);
   updateBuffer();
}

void loop()
{
 a = analogRead(A0);
 b = analogRead(A1);
 c = analogRead(A3);

 acelX = i*250;
 acelY = j*250;
 acelZ = i*250;


 aux = 200*i;
 OILP = aux;

 aux = 5*i;
 ECT = aux;

 aux = 3*i;
 FUELP= aux;

 aux = i*65790;
 ext1 = aux;
 ext2 = 1000*i;
 ext3 = TIMERCOUNT;
 BatCor = i;

 PresFreio_D = 50*i;
 PresFreio_T = 25*i*i;
 if(i>120){
      AcioBomba = 1;
      AcioVent = 0;
      AcioMata = 1;
      AcioSpark = 0;
  }
  else{
      AcioBomba = 0;
      AcioVent = 1;
      AcioMata = 0; 
      AcioSpark = 1; 
  }

 if( i == 255 ){
   i = 0;
 }
 i++;
 if( j == 255 ){
    j = 0;
 }
 j++;
updateBuffer();

Serial.write(buffer1, 20);
if (TIMERCOUNT%2 == 0){
  Serial.write(buffer3, 34);
  Serial.write(buffer2, 36);
}
if(TIMERCOUNT%6 == 0){
  Serial.write(buffer4, 46);
 }
TIMERCOUNT++;
delay(10);
}

void updateBuffer(){
    buffer1[0]= 1;
    buffer1[1]= 5;
    buffer1[2]= acelX >> 8;
    buffer1[3]= acelX;
    buffer1[4]= acelY >> 8;
    buffer1[5]= acelY;
    buffer1[6]= acelZ >> 8;
    buffer1[7]= acelZ;
    buffer1[8]= vel_DD;
    buffer1[9]= vel_DE;
    buffer1[10]= vel_TD;
    buffer1[11]= vel_TE;
    buffer1[12] = velAng;
    buffer1[13]= RPM>>8;
    buffer1[14]= RPM;
    buffer1[15]= Beacon;
    buffer1[16] = TIMERCOUNT>>8;
    buffer1[17] = TIMERCOUNT;
    buffer1[18] = 9;
    buffer1[19] = '\n';

    buffer2[0] = 2;
    buffer2[1] = 5;
    buffer2[2] = ext1 >> 16;
    buffer2[3] = ext1 >> 8;
    buffer2[4] = ext1;
    buffer2[5] = ext2 >> 16;
    buffer2[6] = ext2 >> 8;
    buffer2[7] = ext2;
    buffer2[8] = ext3 >> 16;
    buffer2[9] = ext3 >> 8;
    buffer2[10] = ext3;
    buffer2[11] = ext4 >> 16;
    buffer2[12] = ext4 >> 8;
    buffer2[13] = ext4;
    buffer2[14] = ext5 >> 16;
    buffer2[15] = ext5 >> 8;
    buffer2[16] = ext5;
    buffer2[17] = ext6 >> 16;
    buffer2[18] = ext6 >> 8;
    buffer2[19] = ext6;
    buffer2[20] = ext7 >> 16;
    buffer2[21] = ext7 >> 8;
    buffer2[22] = ext7;
    buffer2[23] = ext8 >> 16;
    buffer2[24] = ext8 >> 8;
    buffer2[25] = ext8;
    buffer2[26] = ext9 >> 16;
    buffer2[27] = ext9 >> 8;
    buffer2[28] = ext9;
    buffer2[29] = ext10 >> 16;
    buffer2[30] = ext10 >> 8;
    buffer2[31] = ext10;
    buffer2[38] = TIMERCOUNT>>8;
    buffer2[39] = TIMERCOUNT; 
    buffer2[40] = 9;
    buffer2[41] = 10; 

    buffer3[0] = 3;
    buffer3[1] = 5;
    buffer3[2] = TPS>>8; // de 0 a 1000, 10bits
    buffer3[3] = TPS;
    buffer3[4] = OILP>>8;
    buffer3[5] = OILP;
    buffer3[6] = FUELP>>8;
    buffer3[7] = FUELP;
    buffer3[8] = VAZBICOS>>8;
    buffer3[9] = VAZBICOS;
    buffer3[10] = PoSus_DE>>8;
    buffer3[11] = PoSus_DE;
    buffer3[12] = PoSus_DD>>8;
    buffer3[13] = PoSus_DD;
    buffer3[14] = PoSus_TE>>8;
    buffer3[15] = PoSus_TE;
    buffer3[16] = PoSus_TD>>8;
    buffer3[17] = PoSus_TD;
    buffer3[18] = PosVolante>>8;
    buffer3[19] = PosVolante;
    buffer3[20] = BatCor>>8;
    buffer3[21] = BatCor;
    buffer3[22] = VentCor>>8;
    buffer3[23] = VentCor;
    buffer3[24] = BombCor>>8;
    buffer3[25] = BombCor;
    buffer3[26]= PresFreio_D>>8;
    buffer3[27] = PresFreio_D;
    buffer3[28]= PresFreio_T>>8;
    buffer3[29] = PresFreio_T;
    buffer3[30] = TIMERCOUNT>>8;
    buffer3[31] = TIMERCOUNT;
    buffer3[32] = 9;
    buffer3[33] = '\n';

    buffer4[0] = 4;
    buffer4[1] = 5;
    buffer4[2] = BAT>>8; //max1500
    buffer4[3] = BAT;
    buffer4[4] = ECT>>8;
    buffer4[5] = ECT;
    buffer4[6] = OILT>>8;
    buffer4[7] = OILT;
    buffer4[8] = Tempdisco_DE>>8;
    buffer4[9] = Tempdisco_DE;
    buffer4[10] = Tempdisco_DD>>8;
    buffer4[11] = Tempdisco_DD;
    buffer4[12] = Tempdisco_TE>>8;
    buffer4[13] = Tempdisco_TE;
    buffer4[14] = Tempdisco_TD>>8;
    buffer4[15] = Tempdisco_TD;
    buffer4[16] = TempVentoinha>>8;
    buffer4[17] = TempVentoinha;
    buffer4[18] = TempBomba>>8;
    buffer4[19] = TempBomba;
    buffer4[20] = PosRunners>>8;
    buffer4[21] = PosRunners;
    buffer4[22] = (AcioVent<<3) | (AcioBomba<<7) | (AcioMata<<5);
    buffer4[23] = GPS_Lat>>16;
    buffer4[24] = GPS_Lat>>8;
    buffer4[25] = GPS_Lat;
    buffer4[26] = GPS_Long>>16;
    buffer4[27] = GPS_Long>>8;
    buffer4[28] = GPS_Long;
    buffer4[29] = GPS_NS;
    buffer4[30] = GPS_EW;
    buffer4[31] = hgpshour;
    buffer4[32] = hgpsminute;
    buffer4[33] = hgpsseconds;
    buffer4[34] = hgpsmilliseconds;
    buffer4[35] = hgpsyear;
    buffer4[36] = hgpsmonth;
    buffer4[37] = hgpsday;
    buffer4[38] = TIMERCOUNT>>8;
    buffer4[39] = TIMERCOUNT;
    buffer4[40] = AcioSpark>>8;
    buffer4[41] = AcioSpark;
    buffer4[42] = TempBat>>8;
    buffer4[43] = TempBat;
    buffer4[44] = 9;
    buffer4[45] = '\n'; 
}
