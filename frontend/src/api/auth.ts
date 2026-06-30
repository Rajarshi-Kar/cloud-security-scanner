import { apiClient } from "./client";
import type { Token, User } from "../types/auth";

export async function login(email: string, password: string): Promise<Token> {
  const { data } = await apiClient.post<Token>("/auth/login", { email, password });
  return data;
}

export async function register(email: string, password: string, full_name: string): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", { email, password, full_name });
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
