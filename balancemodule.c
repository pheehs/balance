#include <Python.h>

// labels for Coin
#define HEAVY 10
#define LIGHT 9
#define SAME 0
#define NONE -1

// results of balance()
#define LEFT_HEAVY 0
#define RIGHT_HEAVY 1
#define BALANCED 2

#define N 13
#define true 1
#define false 0
#define FALSE_HEAVY true
#define COIN_WEIGHT(is_false) ((is_false && FALSE_HEAVY)||(!is_false && !FALSE_HEAVY))? HEAVY:LIGHT

typedef struct{
  int weight;
  int labels[3];
} Coin_t;

typedef struct{
  const int *left;
  const int *right;
} Pair_t;


int balance(Coin_t *coins[N], Pair_t *pair) {
  int lsize,lweight,rsize,rweight,i;
  const int *left, *right;

  left = pair->left;
  right = pair->right;
  
  for(lsize = 0; left[lsize] != -1; lsize++);
  for(rsize = 0; right[rsize] != -1; rsize++);

  lweight = 0;
  for (i = 0; i < lsize; i++)
    lweight += coins[left[i]]->weight;
  rweight = 0;
  for (i = 0; i < rsize; i++)
    rweight += coins[right[i]]->weight;
  
  if (lweight < rweight)
    return RIGHT_HEAVY;
  else if (lweight > rweight)
    return LEFT_HEAVY;
  else
    return BALANCED;
}

void labelCoins(Coin_t *coins[N], const int* i_label, int i_strategy, int label) {
  int size, i;

  for(size = 0; i_label[size] != -1; size++);
  for (i = 0; i < size; i++)
    coins[i_label[i]]->labels[i_strategy] = label;
}

int isSameLabels(Coin_t *coins[N], const int* i_label, int i_strategy) {
  int size, i;
  int label;
  for (size=0; i_label[size] != -1; size++);
  label = coins[i_label[0]]->labels[i_strategy];
  if (label == NONE)
    // whether or not *all* is NONE, single NONE worth experimenting
    return NONE; 
  for (i = 1; i < size; i++) {
    if (coins[i_label[i]]->labels[i_strategy] != label)
      return NONE; // not all is same
  }
  // if all the label were same, return that label
  return label;
}      
    
int run(Pair_t *strategy[3], int false_i) {
  Coin_t *coins[N];
  int i,j;
  int l_samelabel, r_samelabel;

  for (i = 0; i < N; i++) {
    coins[i] = (Coin_t *)malloc(sizeof(Coin_t));
    coins[i]->weight = COIN_WEIGHT(i == false_i);
    coins[i]->labels[0] = NONE;
    coins[i]->labels[1] = NONE;
    coins[i]->labels[2] = NONE;
  }
  for (i = 0; i < 3; i++) {
    for (j = 0; j < i; j++) { // for strategies before
      if (((l_samelabel = isSameLabels(coins, strategy[i]->left, j)) != NONE) && 
	  ((r_samelabel = isSameLabels(coins, strategy[i]->right, j)) != NONE) && 
	  (l_samelabel == r_samelabel) ) {
	// if coins for current experiment have all the same label, 
	// it's not worth experimenting
	//printf("Repeating\n");
	return false; //failure
      }
    } 
    switch ( balance(coins, strategy[i]) ) { // experiment
    case BALANCED:
      labelCoins(coins, strategy[i]->left, i, SAME);
      labelCoins(coins, strategy[i]->right, i, SAME);
      break;
    case RIGHT_HEAVY:
      labelCoins(coins, strategy[i]->left, i, LIGHT);
      labelCoins(coins, strategy[i]->right, i, HEAVY);
      break;
    case LEFT_HEAVY:
      labelCoins(coins, strategy[i]->left, i, HEAVY);
      labelCoins(coins, strategy[i]->right, i, LIGHT);
      break;
    }
  }
  
  // Check if false coin is identical!!
  int n_identical_coins = 0;

  for ( i = 0; i < N; i++) {
    if ((coins[i]->labels[0] == coins[false_i]->labels[0]) &&
	(coins[i]->labels[1] == coins[false_i]->labels[1]) &&
	(coins[i]->labels[2] == coins[false_i]->labels[2]))
      n_identical_coins++;
  }
  if (n_identical_coins == 1) {
    //printf("\nfalse[%d]: %+d,%+d,%+d\n", false_i, coins[false_i]->labels[0],coins[false_i]->labels[1],coins[false_i]->labels[2]);
    //for ( i = 0; i < N; i++) {
    //printf("coin[%d]: %+d,%+d,%+d\n", i, coins[i]->labels[0],coins[i]->labels[1],coins[i]->labels[2]);
    //}
    //printf("OK!\n");
    return true; //this strategy has correct result for this false_i
  }else {
    //printf("Not Identical!\n");
    //n_identical_coins > 1
    return false; //there are many labeled coins same as false one!
  }
}


static PyObject *
balance_run(PyObject *self, PyObject *args)
{

  int *left1 = (int *)malloc(N * sizeof(int));
  int *right1 = (int *)malloc(N * sizeof(int));
  int *left2 = (int *)malloc(N * sizeof(int));
  int *right2 = (int *)malloc(N * sizeof(int));
  int *left3 = (int *)malloc(N * sizeof(int));
  int *right3 = (int *)malloc(N * sizeof(int));
  int i,j;
  //int left1[N],left2[N],left3[N],right1[N],right2[N],right3[N];
  Pair_t *strategy[3];
  unsigned short bit_left1,bit_right1,bit_left2,bit_right2,bit_left3,bit_right3;

  if (!PyArg_ParseTuple(args, "HHHHHH", 
			&bit_left1, &bit_right1, 
			&bit_left2, &bit_right2,
			&bit_left3, &bit_right3)){
    return NULL;
  }
  for (i=j=0; i<N; i++){
    if (bit_left1 & 1) {
      left1[j] = i;
      j++;
    }
    bit_left1 = bit_left1 >> 1;
  }
  left1[j] = -1;

  for (i=j=0; i<N; i++){
    if (bit_right1 & 1) {
      right1[j] = i;
      j++;
    }
    bit_right1 = bit_right1 >> 1;
  }
  right1[j] = -1;

  for (i=j=0; i<N; i++){
    if (bit_left2 & 1) {
      left2[j] = i;
      j++;
    }
    bit_left2 = bit_left2 >> 1;
  }
  left2[j] = -1;

  for (i=j=0; i<N; i++){
    if (bit_right2 & 1) {
      right2[j] = i;
      j++;
    }
    bit_right2 = bit_right2 >> 1;
  }
  right2[j] = -1;
  for (i=j=0; i<N; i++){
    if (bit_left3 & 1) {
      left3[j] = i;
      j++;
    }
    bit_left3 = bit_left3 >> 1;
  }
  left3[j] = -1;

  for (i=j=0; i<N; i++){
    if (bit_right3 & 1) {
      right3[j] = i;
      j++;
    }
    bit_right3 = bit_right3 >> 1;
  }
  right3[j] = -1;

  strategy[0] = (Pair_t *)malloc(sizeof(Pair_t));
  strategy[0]->left = left1;
  strategy[0]->right = right1;
  strategy[1] = (Pair_t *)malloc(sizeof(Pair_t));
  strategy[1]->left = left2;
  strategy[1]->right = right2;
  strategy[2] = (Pair_t *)malloc(sizeof(Pair_t));
  strategy[2]->left = left3;
  strategy[2]->right = right3;

  for (i = 0; i < N; i++) {
    if (run(strategy, i) == false)
      return Py_BuildValue("i", 1);
  }
  return Py_BuildValue("i", 0);// succeed for all false_i
}

static PyObject *
hello(PyObject *self)
{
    printf("Hello World!!\n");
    Py_RETURN_NONE;
}

static char ext_doc[] = "C extention module example\n";

static PyMethodDef methods[] = {
  {"hello", (PyCFunction)hello, METH_NOARGS, "print hello world.\n"},
  {"balance_run", balance_run, METH_VARARGS, "simulate balance.\n"},
  {NULL, NULL, 0, NULL}
};

void initbalancemodule(void)
{
    Py_InitModule3("balancemodule", methods, ext_doc);
}
