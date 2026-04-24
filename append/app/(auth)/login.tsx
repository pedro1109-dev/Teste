import { AntDesign } from '@expo/vector-icons';
import { apiFetch } from '../../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  SafeAreaView,
  TouchableOpacity,
  StatusBar,
  ScrollView,
  Linking,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import CustomInput from '../../components/ui/CustomInput';
import PrimaryButton from '../../components/ui/PrimaryButton';
import { theme } from '../../constants/theme';

const API_URL = 'https://projeto-sustentavel-0-1.onrender.com';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [carregando, setCarregando] = useState(false);

  async function salvarUsuarioGoogle(url: string) {
    try {
      const parsedUrl = new URL(url);

      const id = parsedUrl.searchParams.get('id');
      const nome = parsedUrl.searchParams.get('nome');
      const emailGoogle = parsedUrl.searchParams.get('email');

      if (!id || !nome || !emailGoogle) return;

      const usuarioGoogle = {
        id,
        nome,
        email: emailGoogle,
      };

      await AsyncStorage.setItem('usuario', JSON.stringify(usuarioGoogle));
      await AsyncStorage.setItem('usuario_id', String(id));

      router.replace('/(tabs)/home');
    } catch (error) {
      console.log('Erro ao salvar login Google:', error);
    }
  }

  useEffect(() => {
    if (Platform.OS === 'web') {
      salvarUsuarioGoogle(window.location.href);
    }

    const subscription = Linking.addEventListener('url', ({ url }) => {
      salvarUsuarioGoogle(url);
    });

    Linking.getInitialURL().then((url) => {
      if (url) salvarUsuarioGoogle(url);
    });

    return () => subscription.remove();
  }, []);

  const entrarComGoogle = async () => {
    try {
      await Linking.openURL(`${API_URL}/login/google`);
    } catch (error) {
      alert('Erro ao abrir login com Google.');
    }
  };

  const entrar = async () => {
    if (carregando) return;

    if (!email || !senha) {
      alert('Preencha email e senha.');
      return;
    }

    try {
      setCarregando(true);

      const usuarioLogado = await apiFetch('/login', {
        method: 'POST',
        body: JSON.stringify({ email, senha }),
      });

      await AsyncStorage.setItem('usuario', JSON.stringify(usuarioLogado));
      await AsyncStorage.setItem('usuario_id', String(usuarioLogado.id));

      router.replace('/(tabs)/home');
    } catch (error: any) {
      alert(
        error?.data?.detail ||
          error?.data?.message ||
          error?.message ||
          'Erro ao fazer login.'
      );
    } finally {
      setCarregando(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" />

      <LinearGradient
        colors={[
          theme.colors.backgroundTop,
          theme.colors.backgroundMid,
          theme.colors.backgroundBottom,
        ]}
        style={styles.container}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.topArea}>
            <Image
              source={require('../../assets/images/logo.png')}
              style={styles.logo}
              resizeMode="contain"
            />

            <Text style={styles.brandText}>
              <Text style={styles.brandWhite}>Eco</Text>
              <Text style={styles.brandGreen}>Control</Text>
            </Text>

            <View style={styles.brandGlowLine} />
          </View>

          <View style={styles.card}>
            <Text style={styles.title}>Login</Text>
            <View style={styles.titleUnderline} />

            <CustomInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              placeholder="Digite seu email"
              icon="mail"
            />

            <CustomInput
              label="Senha"
              value={senha}
              onChangeText={setSenha}
              placeholder="Digite sua senha"
              secureTextEntry
              icon="lock"
              isPassword
            />

            <TouchableOpacity onPress={() => router.push('/(auth)/recuperar-senha')}>
              <Text style={styles.forgotPassword}>Esqueci minha senha</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => router.push('/(auth)/cadastro')}>
              <Text style={styles.link}>
                Não possui cadastro?{' '}
                <Text style={styles.linkHighlight}>Clique aqui</Text>
              </Text>
            </TouchableOpacity>
          </View>

          <PrimaryButton
            title={carregando ? 'Entrando...' : 'Entrar'}
            onPress={entrar}
          />

          <View style={styles.dividerArea}>
            <View style={styles.divider} />
            <Text style={styles.dividerText}>ou</Text>
            <View style={styles.divider} />
          </View>

          <TouchableOpacity style={styles.googleButton} onPress={entrarComGoogle}>
            <Text style={styles.googleLogo}>G</Text>
            <Text style={styles.googleButtonText}>Continuar com Google</Text>
          </TouchableOpacity>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  container: { flex: 1 },

  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingVertical: 30,
  },

  topArea: {
    alignItems: 'center',
    marginBottom: 24,
  },

  logo: {
    width: 110,
    height: 110,
    transform: [{ translateY: 20 }],
  },

  brandText: {
    fontSize: 30,
    fontWeight: '900',
  },

  brandWhite: { color: theme.colors.brandWhite },
  brandGreen: { color: theme.colors.brandGreen },

  brandGlowLine: {
    width: 140,
    height: 5,
    borderRadius: 999,
    backgroundColor: 'rgba(90,255,120,0.25)',
    marginTop: 6,
  },

  card: {
    backgroundColor: theme.colors.card,
    borderRadius: 30,
    borderWidth: 1,
    borderColor: theme.colors.cardBorder,
    padding: 24,
    marginTop: 10,
  },

  title: {
    color: theme.colors.text,
    fontSize: 32,
    fontWeight: '900',
  },

  titleUnderline: {
    width: 80,
    height: 5,
    borderRadius: 999,
    backgroundColor: theme.colors.accent,
    marginBottom: 20,
    marginTop: 6,
  },

  link: {
    color: theme.colors.textSoft,
    fontSize: 12,
    marginTop: 6,
  },

  linkHighlight: {
    color: theme.colors.accentStrong,
    fontWeight: '800',
  },

  forgotPassword: {
    color: theme.colors.accentStrong,
    fontSize: 12,
    fontWeight: '800',
    textAlign: 'right',
    marginTop: 6,
    marginBottom: 10,
  },

  dividerArea: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 16,
  },

  divider: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.25)',
  },

  dividerText: {
    color: theme.colors.textSoft,
    marginHorizontal: 12,
    fontWeight: '700',
  },

  googleButton: {
    height: 58,
    borderRadius: 18,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    marginTop: 4,
    shadowColor: '#000',
    shadowOpacity: 0.25,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 5 },
    elevation: 6,
  },

  googleLogo: {
    width: 30,
    height: 30,
    borderRadius: 15,
    textAlign: 'center',
    lineHeight: 30,
    fontSize: 20,
    fontWeight: '900',
    color: '#4285F4',
    backgroundColor: '#F5F5F5',
  },

  googleButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '900',
  },
});