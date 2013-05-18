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
