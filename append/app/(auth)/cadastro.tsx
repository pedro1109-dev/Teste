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

export default function Cadastro() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');

  async function salvarUsuarioGoogle(url: string) {
    try {
      const parsedUrl = new URL(url);
      const id = parsedUrl.searchParams.get('id');
      const nomeGoogle = parsedUrl.searchParams.get('nome');
      const emailGoogle = parsedUrl.searchParams.get('email');

      if (!id || !nomeGoogle || !emailGoogle) return;

      const usuarioGoogle = {
        id,
        nome: nomeGoogle,
        email: emailGoogle,
      };

      await AsyncStorage.setItem('usuario', JSON.stringify(usuarioGoogle));
      await AsyncStorage.setItem('usuario_id', String(id));

      router.replace('/(tabs)/home');
    } catch (error) {
      console.log('Erro ao salvar cadastro Google:', error);
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

  const continuarComGoogle = async () => {
    try {
      await Linking.openURL(`${API_URL}/login/google`);
    } catch (error) {
      alert('Erro ao abrir cadastro com Google.');
    }
  };

  const handleCadastro = async () => {
    if (!nome || !email || !senha || !confirmarSenha) {
      alert('Preencha todos os campos');
      return;
    }

    if (senha !== confirmarSenha) {
      alert('As senhas não coincidem');
      return;
    }

    try {
      await apiFetch('/Usuario/registrar', {
        method: 'POST',
        body: JSON.stringify({
          nome,
          email,
          senha,
        }),
      });

      alert('Cadastro realizado com sucesso!');
      router.replace('/(auth)/login');
    } catch (error: any) {
      console.log('ERRO CADASTRO:', error);

      const mensagem =
        error?.data?.detail ||
        error?.data?.message ||
        error?.message ||
        'Erro ao cadastrar usuário.';

      alert(typeof mensagem === 'string' ? mensagem : JSON.stringify(mensagem));
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
            <Text style={styles.title}>Cadastro</Text>
            <View style={styles.titleUnderline} />

            <CustomInput
              label="Nome"
              value={nome}
              onChangeText={setNome}
              placeholder="Digite seu nome"
              icon="user"
            />

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

            <CustomInput
              label="Confirmar senha"
              value={confirmarSenha}
              onChangeText={setConfirmarSenha}
              placeholder="Confirme sua senha"
              secureTextEntry
              icon="shield"
              isPassword
            />

            <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
              <Text style={styles.link}>
                Já possui cadastro? <Text style={styles.linkHighlight}>Entrar</Text>
              </Text>
            </TouchableOpacity>
          </View>
          

          <PrimaryButton title="Cadastrar" onPress={handleCadastro} />

          <View style={styles.dividerArea}>
            <View style={styles.divider} />
            <Text style={styles.dividerText}>ou</Text>
            <View style={styles.divider} />
          </View>
          <TouchableOpacity style={styles.googleButton} onPress={continuarComGoogle}>
            <View style={styles.googleContent}>
              <AntDesign name="google" size={20} color="#DB4437" />
              <Text style={styles.googleButtonText}>Continuar com o Google</Text>
            </View>
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
    marginTop: 0,
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
    fontSize: 30,
    fontWeight: '900',
  },

  titleUnderline: {
    width: 110,
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
  height: 52,
  borderRadius: 8,
  backgroundColor: '#FFFFFF',
  borderWidth: 1,
  borderColor: '#DADCE0',
  justifyContent: 'center',
  marginTop: 12,
},

googleContent: {
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 10,
},

googleButtonText: {
  color: '#f7f7f7',
  fontSize: 15,
  fontWeight: '500',
},
});