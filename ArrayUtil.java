public class ArrayUtil {
        public static Object[] map(Object[] array, Method method) {
            for (int i = 0; i < array.length; i++) {
                array[i] = method.invoke(array[i]);
            }
            return array;
        }

        /**
         * @param <IType> Input type specification
         * @param <RType> Return type specification
         */
        public static interface Method<IType, RType> {
            public RType invoke(IType v);
        }
    }
/*
Usage:
public static void main(String[] args) {
        Object[] a = {2, 4, 5, 6};
        System.out.println(Arrays.toString(ArrayUtil.map(a, new ArrayUtil.Method<Integer, String>() {
            @Override
            public String invoke(Integer v) {
                return "value=" + v;  //To change body of implemented methods use File | Settings | File Templates.
            }
        })));
    }
   */
